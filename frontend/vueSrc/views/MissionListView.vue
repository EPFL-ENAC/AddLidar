<template>
  <div class="mission-list-container">
    <div class="header">
      <h1>Available Missions</h1>
      <p>Select a mission to view its LiDAR data</p>
    </div>

    <div v-if="isLoading" class="loading">
      <div class="loading-spinner"></div>
      <div class="q-mt-sm">Loading missions...</div>
    </div>

    <div v-else-if="error" class="error">
      <div class="error-icon">⚠️</div>
      <div class="q-mt-sm">{{ error }}</div>
    </div>

    <div v-else class="missions-grid">
      <div
        v-for="mission in enrichedMissions"
        :key="mission.mission_key"
        class="mission-card"
        :class="{ 'mission-pending': mission.processing_status === 'pending' }"
        @click="viewMission(mission.mission_key)"
      >
        <div class="mission-status">
          <span
            class="status-badge"
            :class="`status-${mission.processing_status || 'unknown'}`"
          >
            {{ formatStatus(mission.processing_status) }}
          </span>
        </div>

        <div class="mission-info">
          <h3>{{ mission.mission_key }}</h3>
          <p class="mission-details">
            <strong>Output:</strong> {{ mission.output_path }}<br />
            <strong>Last Checked:</strong>
            {{ formatDate(mission.last_checked_time) }}<br />
            <span v-if="mission.last_processed_time">
              <strong>Processed:</strong>
              {{ formatDate(mission.last_processed_time) }}
            </span>
            <span v-else> <strong>Status:</strong> Not yet processed </span>
          </p>

          <div v-if="mission.metadata" class="metadata-info">
            <p>
              <strong>Points:</strong> {{ formatNumber(mission.metadata.points)
              }}<br />
              <strong>Bounds:</strong>
              {{ formatBounds(mission.metadata.boundingBox) }}
            </p>
          </div>

          <div class="mission-actions">
            <button class="view-btn" @click="viewMission(mission.mission_key)">
              View Mission
            </button>
          </div>
        </div>

        <div v-if="mission.error_message" class="error-message">
          <strong>Error:</strong> {{ mission.error_message }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { useDirectoryStore } from "@/stores/directoryStore";

const router = useRouter();
const directoryStore = useDirectoryStore();

const missions = ref([]);
const isLoading = ref(true);
const error = ref(null);

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
            mission.mission_key
          );
        } catch (err) {
          console.warn(
            `Failed to load metadata for mission ${mission.mission_key}:`,
            err
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
    1
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
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 30px;
}

.loading,
.error {
  text-align: center;
  padding: 40px;
}

.missions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.mission-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: white;
  position: relative;
}

.mission-card:hover:not(.mission-pending) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.mission-pending {
  opacity: 0.7;
}

.mission-status {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 1;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-pending {
  background: #ff9800;
  color: white;
}

.status-completed,
.status-processed {
  background: #4caf50;
  color: white;
}

.status-error {
  background: #f44336;
  color: white;
}

.status-unknown {
  background: #9e9e9e;
  color: white;
}

.mission-info {
  padding: 15px;
  padding-top: 35px; /* Account for status badge */
}

.mission-info h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.mission-details {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.4;
}

.metadata-info {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.metadata-info p {
  margin: 0;
  font-size: 13px;
  color: #555;
}

.mission-actions {
  text-align: right;
}

.view-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.view-btn:hover:not(:disabled) {
  background: #0056b3;
}

.view-btn:disabled {
  background: #ccc;
}

.error-message {
  background: #ffebee;
  color: #c62828;
  padding: 10px;
  border-top: 1px solid #ffcdd2;
  font-size: 13px;
}
</style>
