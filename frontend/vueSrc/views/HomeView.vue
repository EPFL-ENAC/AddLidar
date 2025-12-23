<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import {
  useDirectoryStore,
  type PotreeMetacloudState,
} from "@/stores/directoryStore";
import MainAppLayout from "@/layouts/MainAppLayout.vue";
import MissionFootprintMap from "@/components/MissionFootprintMap.vue";
import MissionListPanel from "@/components/MissionListPanel.vue";

interface MissionWithMetadata extends PotreeMetacloudState {
  metadata?: {
    points?: number;
    boundingBox?: {
      min: [number, number];
      max: [number, number];
    };
  } | null;
}

const router = useRouter();
const directoryStore = useDirectoryStore();

const missions = ref<MissionWithMetadata[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const selectedMission = ref<string | null>(null);
const hoveredMission = ref<string | null>(null);
const zoomToMission = ref<string | null>(null);
const hiddenMissions = ref<Set<string>>(new Set());

const enrichedMissions = computed(() => missions.value);

async function loadMissions() {
  try {
    isLoading.value = true;
    error.value = null;

    const missionData: PotreeMetacloudState[] =
      await directoryStore.fetchAllMissions();

    const missionPromises = missionData.map(async (mission) => {
      let metadata = null;
      if (
        mission.processing_status !== "pending" &&
        mission.processing_status !== "error"
      ) {
        try {
          const response = await fetch(
            `${directoryStore.staticBasePath}/Potree/${mission.mission_key}/metadata.json`,
          );
          if (response.ok) metadata = await response.json();
        } catch {
          // Metadata not available
        }
      }
      return { ...mission, metadata };
    });

    missions.value = await Promise.all(missionPromises);
  } catch (err) {
    error.value =
      err instanceof Error ? err.message : "Failed to load missions";
  } finally {
    isLoading.value = false;
  }
}

function onMissionSelect(missionKey: string) {
  selectedMission.value = missionKey;
  zoomToMission.value = missionKey;
  setTimeout(() => (zoomToMission.value = null), 100);
}

function onMissionHover(missionKey: string | null) {
  hoveredMission.value = missionKey;
}

function viewMission(missionKey: string) {
  router.push(`/viewer/${missionKey}`);
}

function onHiddenMissionsChange(hidden: Set<string>) {
  hiddenMissions.value = hidden;
}

onMounted(() => {
  directoryStore.configurePaths("/api", "/static");
  loadMissions();
});
</script>

<template>
  <main-app-layout>
    <template #sidebar>
      <!-- Loading State -->
      <div v-if="isLoading" class="flex flex-center column q-pa-xl">
        <q-spinner color="primary" size="48px" />
        <p class="q-mt-md text-grey-6">Loading missions...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex flex-center column q-pa-xl">
        <q-icon name="error_outline" color="negative" size="64px" />
        <p class="q-mt-md text-negative">{{ error }}</p>
        <q-btn flat color="primary" label="Retry" @click="loadMissions" />
      </div>

      <!-- Mission List -->
      <mission-list-panel
        v-else
        :missions="enrichedMissions"
        :selected-mission="selectedMission"
        :hovered-mission="hoveredMission"
        @select="onMissionSelect"
        @hover="onMissionHover"
        @explore="viewMission"
        @hidden-missions-change="onHiddenMissionsChange"
      />
    </template>

    <template #content>
      <mission-footprint-map
        v-if="!isLoading && !error"
        :missions="enrichedMissions"
        :selected-mission="selectedMission"
        :hovered-mission="hoveredMission"
        :zoom-to-mission="zoomToMission"
        :hidden-missions="hiddenMissions"
        @mission-select="onMissionSelect"
        @mission-hover="onMissionHover"
      />
    </template>
  </main-app-layout>
</template>

<style scoped>
/* Styles are now handled by MainAppLayout */
</style>
