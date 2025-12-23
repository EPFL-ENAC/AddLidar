<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import {
  useDirectoryStore,
  type PotreeMetacloudState,
} from "@/stores/directoryStore";
import DefaultLayout from "@/layouts/DefaultLayout.vue";
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

onMounted(() => {
  directoryStore.configurePaths("/api", "/static");
  loadMissions();
});
</script>

<template>
  <default-layout>
    <q-page class="home-page">
      <!-- Loading State -->
      <div v-if="isLoading" class="flex flex-center column full-height">
        <q-spinner color="primary" size="48px" />
        <p class="q-mt-md text-grey-6">Loading missions...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="flex flex-center column full-height">
        <q-icon name="error_outline" color="negative" size="64px" />
        <p class="q-mt-md text-negative">{{ error }}</p>
        <q-btn flat color="primary" label="Retry" @click="loadMissions" />
      </div>

      <!-- Content -->
      <div v-else class="home-content">
        <!-- Map -->
        <div class="home-map">
          <mission-footprint-map
            :missions="enrichedMissions"
            :selected-mission="selectedMission"
            :hovered-mission="hoveredMission"
            :zoom-to-mission="zoomToMission"
            @mission-select="onMissionSelect"
            @mission-hover="onMissionHover"
          />
        </div>

        <!-- Mission List Panel -->
        <mission-list-panel
          class="home-sidebar"
          :missions="enrichedMissions"
          :selected-mission="selectedMission"
          :hovered-mission="hoveredMission"
          @select="onMissionSelect"
          @hover="onMissionHover"
          @explore="viewMission"
        />
      </div>
    </q-page>
  </default-layout>
</template>

<style scoped>
.home-page {
  height: calc(100vh - var(--header-height));
}

.home-content {
  display: flex;
  height: 100%;
}

.home-map {
  flex: 1;
  min-width: 0;
}

.home-sidebar {
  width: 600px;
}

@media (max-width: 900px) {
  .home-content {
    flex-direction: column;
  }

  .home-map {
    height: 300px;
  }

  .home-sidebar {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--border-color);
  }
}
</style>
