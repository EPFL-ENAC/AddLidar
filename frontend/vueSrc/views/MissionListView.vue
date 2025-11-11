<template>
  <div
    class="q-pa-md"
    style="height: 100vh; display: flex; flex-direction: column"
  >
    <div v-if="isLoading" class="flex flex-center column" style="flex: 1">
      <q-spinner color="primary" size="40px" />
      <div class="q-mt-sm text-grey-6">Loading missions...</div>
    </div>

    <div v-else-if="error" class="flex flex-center column" style="flex: 1">
      <q-icon name="warning" color="negative" size="48px" />
      <div class="q-mt-sm text-negative">{{ error }}</div>
    </div>

    <div v-else class="row" style="flex: 1; gap: 20px; min-height: 0">
      <!-- Map on the left -->
      <div
        class="col"
        style="
          min-width: 400px;
          border: 1px solid #ddd;
          border-radius: 8px;
          overflow: hidden;
        "
      >
        <mission-footprint-map
          :missions="enrichedMissions"
          :selected-mission="selectedMission"
          :zoom-to-mission="zoomToMission"
          @mission-select="onMissionSelect"
          @mission-hover="onMissionHover"
        />
      </div>

      <!-- Mission list on the right -->
      <div class="col-4 column">
        <div class="q-mb-md q-pb-md" style="border-bottom: 2px solid #f0f0f0">
          <div class="row items-center justify-between q-mb-xs">
            <h2 class="text-h5 q-ma-none text-weight-medium">
              AddLidar - Missions
            </h2>
            <div class="row items-center q-gutter-xs">
              <q-badge
                color="primary"
                :label="enrichedMissions.length"
                rounded
              />
              <span class="text-caption text-grey-6">
                {{ enrichedMissions.length === 1 ? "mission" : "missions" }}
                available
              </span>
            </div>
          </div>
          <p class="q-ma-none text-caption text-grey-6 text-italic">
            Click on the map or select a mission card below to explore LiDAR
            data
          </p>
        </div>

        <q-scroll-area class="mission-scroll-area q-pa-md">
          <mission-card
            v-for="mission in enrichedMissions"
            :key="mission.mission_key"
            :mission="mission"
            :is-selected="mission.mission_key === selectedMission"
            :is-hovered="mission.mission_key === hoveredMission"
            @click="onMissionSelect"
            @hover="onMissionHover"
            @view="viewMission"
          />

          <div v-if="enrichedMissions.length === 0" class="text-center q-pa-xl">
            <q-icon
              name="folder_open"
              color="grey-5"
              size="64px"
              class="q-mb-md"
              style="opacity: 0.7"
            />
            <div class="text-body1 text-weight-medium text-grey-7 q-mb-xs">
              No missions available
            </div>
            <div class="text-caption text-grey-5 text-italic">
              Check back later or contact your administrator
            </div>
          </div>
        </q-scroll-area>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useDirectoryStore } from "@/stores/directoryStore";
import MissionFootprintMap from "@/components/MissionFootprintMap.vue";
import MissionCard from "@/components/MissionCard.vue";

const router = useRouter();
const directoryStore = useDirectoryStore();

const missions = ref([]);
const isLoading = ref(true);
const error = ref(null);
const selectedMission = ref(null);
const hoveredMission = ref(null);
const zoomToMission = ref(null);

// Computed property to enrich missions with metadata
const enrichedMissions = computed(() => {
  return missions.value.map((mission) => ({
    ...mission,
    metadata: mission.metadata || null,
  }));
});

// Load mission data
async function loadMissions() {
  try {
    isLoading.value = true;
    error.value = null;

    // Fetch all missions from the API
    const missionData = await directoryStore.fetchAllMissions();

    // Try to load metadata for each mission (only for processed ones)
    const missionPromises = missionData.map(async (mission) => {
      let metadata = null;

      // Only try to fetch metadata for processed missions
      if (
        mission.processing_status !== "pending" &&
        mission.processing_status !== "error"
      ) {
        try {
          metadata = await directoryStore.fetchPointcloudMetadata(
            mission.mission_key,
          );
        } catch (err) {
          console.warn(
            `Failed to load metadata for mission ${mission.mission_key}:`,
            err,
          );
        }
      }

      return {
        ...mission,
        metadata,
      };
    });

    missions.value = await Promise.all(missionPromises);
  } catch (err) {
    error.value = err.message || "Failed to load missions";
    console.error("Error loading missions:", err);
  } finally {
    isLoading.value = false;
  }
}

// Handle mission selection from map or card
function onMissionSelect(missionKey) {
  selectedMission.value = missionKey;
  // Trigger zoom to the selected mission
  zoomToMission.value = missionKey;
  // Reset zoom trigger after a short delay to allow for future zoom requests
  setTimeout(() => {
    zoomToMission.value = null;
  }, 100);
}

// Handle mission hover from map or card
function onMissionHover(missionKey) {
  hoveredMission.value = missionKey;
}

function viewMission(missionKey) {
  console.log("Viewing mission:", missionKey, missions.value);
  // Only allow viewing if not pending
  const mission = missions.value.find((m) => m.mission_key === missionKey);
  if (mission) {
    router.push(`/mission/${missionKey}`);
  }
}

function formatStatus(status) {
  if (!status) return "Unknown";
  return status.charAt(0).toUpperCase() + status.slice(1);
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleString();
}

function formatNumber(num) {
  if (!num) return "N/A";
  return new Intl.NumberFormat().format(num);
}

function formatBounds(boundingBox) {
  if (!boundingBox) return "N/A";
  const { min, max } = boundingBox;
  return `[${min[0].toFixed(1)}, ${min[1].toFixed(1)}] to [${max[0].toFixed(
    1,
  )}, ${max[1].toFixed(1)}]`;
}

onMounted(() => {
  // Configure paths (adjust these based on your deployment)
  directoryStore.configurePaths("/api", "/static");
  loadMissions();
});
</script>

<style scoped>
/* Responsive design */
@media (max-width: 1024px) {
  .row {
    flex-direction: column !important;
  }

  .col {
    height: 400px;
    min-width: auto !important;
  }

  .col-4 {
    min-width: auto !important;
  }
}

@media (max-width: 768px) {
  .col {
    height: 300px;
  }
}

.mission-scroll-area {
  border-radius: 0.3rem;
  flex: 1;
}
</style>
