<template>
  <div class="mission-list-container">
    <div v-if="isLoading" class="loading">
      <div class="loading-spinner"></div>
      <div class="q-mt-sm">Loading missions...</div>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <div class="q-mt-sm">{{ error }}</div>
    </div>

    <div v-else class="missions-layout">
      <!-- Map on the left -->
      <div class="map-section">
        <mission-footprint-map
          :missions="enrichedMissions"
          :selected-mission="selectedMission"
          :zoom-to-mission="zoomToMission"
          @mission-select="onMissionSelect"
          @mission-hover="onMissionHover"
        />
      </div>

      <!-- Mission list on the right -->
      <div class="missions-section">
        <div class="missions-header">
          <div class="header-content">
            <h2>AddLidar - Missions</h2>
            <div class="mission-count">
              <span class="count-badge">{{ enrichedMissions.length }}</span>
              <span class="count-text"
                >{{
                  enrichedMissions.length === 1 ? "mission" : "missions"
                }}
                available</span
              >
            </div>
          </div>
          <p class="header-subtitle">
            Click on the map or select a mission card below to explore LiDAR
            data
          </p>
        </div>

        <div class="missions-list">
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

          <div v-if="enrichedMissions.length === 0" class="no-missions">
            <div class="no-missions-icon">📂</div>
            <div class="no-missions-text">No missions available</div>
            <div class="no-missions-subtitle">
              Check back later or contact your administrator
            </div>
          </div>
        </div>
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
.mission-list-container {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  text-align: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.header h1 {
  margin: 0 0 10px 0;
  color: #333;
}

.header p {
  margin: 0;
  color: #666;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.missions-layout {
  flex: 1;
  display: flex;
  gap: 20px;
  min-height: 0; /* Important for flex children */
}

.map-section {
  flex: 2;
  min-width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.missions-section {
  flex: 1;
  min-width: 350px;
  display: flex;
  flex-direction: column;
}

.missions-header {
  margin-bottom: 20px;
  padding-bottom: 18px;
  border-bottom: 2px solid #f0f0f0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.missions-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 22px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mission-count {
  display: flex;
  align-items: center;
  gap: 8px;
}

.count-badge {
  background: #007bff;
  color: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  min-width: 20px;
  text-align: center;
}

.count-text {
  color: #6c757d;
  font-size: 13px;
  font-weight: 500;
}

.header-subtitle {
  margin: 0;
  color: #6c757d;
  font-size: 14px;
  font-style: italic;
  line-height: 1.4;
}

.missions-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 10px;
}

.missions-list::-webkit-scrollbar {
  width: 6px;
}

.missions-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.missions-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.missions-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.no-missions {
  text-align: center;
  padding: 60px 20px;
  color: #6c757d;
}

.no-missions-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.7;
}

.no-missions-text {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #495057;
}

.no-missions-subtitle {
  font-size: 14px;
  color: #adb5bd;
  font-style: italic;
}

/* Responsive design */
@media (max-width: 1024px) {
  .missions-layout {
    flex-direction: column;
  }

  .map-section {
    height: 400px;
    min-width: auto;
  }

  .missions-section {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .mission-list-container {
    padding: 10px;
  }

  .missions-layout {
    gap: 15px;
  }

  .map-section {
    height: 300px;
  }

  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .missions-header h2 {
    font-size: 20px;
  }

  .mission-count {
    align-self: flex-end;
  }

  .header-subtitle {
    font-size: 13px;
  }
}
</style>
