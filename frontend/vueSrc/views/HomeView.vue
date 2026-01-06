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
import AboutContent from "@/components/AboutContent.vue";
import { useAppMeta } from "@/composables/useMeta";

useAppMeta({ title: "Browse Missions" });

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

const showAbout = ref(false);
const missions = ref<MissionWithMetadata[]>([]);
const isLoading = ref(true);
const error = ref<string | null>(null);
const selectedMission = ref<string | null>(null);
const hoveredMission = ref<string | null>(null);
const zoomToMission = ref<string | null>(null);
const hiddenMissions = ref<Set<string>>(new Set());
const visibleMissions = ref<string[]>([]);
const autoFilterEnabled = ref(false);

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

function onMissionSelect(missionKey: string | null) {
  if (missionKey === null) {
    // Deselect
    selectedMission.value = null;
    zoomToMission.value = null;
  } else {
    selectedMission.value = missionKey;
    zoomToMission.value = missionKey;
    setTimeout(() => (zoomToMission.value = null), 100);
  }
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

function onVisibleMissionsChange(missionKeys: string[]) {
  visibleMissions.value = missionKeys;
}

function onAutoFilterToggle(enabled: boolean) {
  autoFilterEnabled.value = enabled;
}

function toggleAbout() {
  showAbout.value = !showAbout.value;
}

onMounted(() => {
  directoryStore.configurePaths("/api", "/static");
  loadMissions();
});
</script>

<template>
  <main-app-layout>
    <template #sidebar>
      <div class="column full-height q-pt-md">
        <!-- Header with title and About link -->
        <header v-if="!isLoading && !error" class="q-pa-md q-pb-sm">
          <div class="row items-center justify-between">
            <h1
              class="text-subtitle2 text-weight-medium text-uppercase q-ma-none"
            >
              {{ showAbout ? "About AddLidar" : "Missions" }}
            </h1>
            <q-btn flat v-if="!showAbout" label="About" @click="toggleAbout" />
            <q-btn flat v-else icon="close" @click="toggleAbout" />
          </div>
        </header>

        <!-- Loading State -->
        <div v-if="isLoading" class="col flex flex-center column">
          <q-spinner color="primary" size="48px" />
          <p class="q-mt-md text-grey-6">Loading missions...</p>
        </div>

        <!-- Error State -->
        <div v-else-if="error" class="col flex flex-center column">
          <q-icon name="error_outline" color="negative" size="64px" />
          <p class="q-mt-md text-negative">{{ error }}</p>
          <q-btn flat color="primary" label="Retry" @click="loadMissions" />
        </div>

        <!-- About Content or Mission List -->
        <template v-else>
          <about-content v-if="showAbout" class="col" @close="toggleAbout" />
          <mission-list-panel
            v-else
            class="col"
            :missions="enrichedMissions"
            :selected-mission="selectedMission"
            :hovered-mission="hoveredMission"
            :visible-missions="visibleMissions"
            :auto-filter="autoFilterEnabled"
            @select="onMissionSelect"
            @hover="onMissionHover"
            @explore="viewMission"
            @hidden-missions-change="onHiddenMissionsChange"
            @auto-filter-toggle="onAutoFilterToggle"
          />
        </template>

        <!-- Footer -->
        <div class="q-pa-md q-pt-sm text-center">
          <small class="text-grey-6">
            &copy; 2025 EPFL - École Polytechnique Fédérale de Lausanne
          </small>
        </div>
      </div>
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
        @visible-missions-change="onVisibleMissionsChange"
      />
    </template>
  </main-app-layout>
</template>

<style scoped>
/* Styles are now handled by MainAppLayout */
</style>
