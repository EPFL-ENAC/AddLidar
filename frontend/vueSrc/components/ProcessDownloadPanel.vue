<template>
  <div>
    <q-form class="q-gutter-md" @submit.prevent="onSubmit">
      <q-select
        outlined
        label="Format"
        v-model="format"
        :options="formatOptions"
        hint="Select output file format"
      />
      <q-select
        outlined
        label="EPSG Code"
        :options="epsgOptions"
        v-model="epsg"
        placeholder="EPSG Code (optional)"
        hint="Coordinate reference system"
      />
      <clip-volume />

      <q-input
        outlined
        type="number"
        label="Number of points"
        v-model="number"
        placeholder="Number of points (optional)"
        hint="Limit the total number of points"
      />

      <q-btn
        label="Generate processing request"
        class="full-width"
        size="md"
        outline
        type="submit"
        color="primary"
        :loading="processing"
      >
        <template v-slot:loading>
          <q-spinner-gears class="on-left" />
          Starting job...
        </template>
      </q-btn>
    </q-form>

    <!-- Status and progress section -->
    <div v-if="currentJob" class="q-mt-md">
      <q-separator class="q-my-md" />

      <div class="text-h6">Job Status</div>
      <div class="q-mt-sm q-pa-sm bg-grey-1 rounded-borders">
        <div class="row items-center">
          <div class="col">
            <div><strong>Job ID:</strong> {{ currentJob.job_name }}</div>
            <div><strong>Status:</strong> {{ jobStatus }}</div>
            <div v-if="jobProgress > 0">
              <strong>Progress:</strong>
              {{ Math.floor(jobProgress * 100) }}%
            </div>
          </div>
          <div class="col-auto">
            <!-- Show checkmark when job is complete -->
            <q-icon
              v-if="
                jobStatus === 'Complete' || jobStatus === 'SuccessCriteriaMet'
              "
              name="check_circle"
              color="positive"
              size="md"
              class="q-ml-md"
            />
            <!-- Show error icon when there's an error -->
            <q-icon
              v-else-if="jobStatus === 'Error'"
              name="error"
              color="negative"
              size="md"
              class="q-ml-md"
            />
            <!-- Show progress spinner otherwise -->
            <q-circular-progress
              v-else
              size="md"
              indeterminate
              color="secondary"
              track-color="grey-3"
              class="q-ml-md"
            />
          </div>
        </div>

        <!-- Progress bar for running jobs with detailed info -->
        <div v-if="jobStatus === 'Running' && progressInfo" class="q-mt-md">
          <q-linear-progress
            :value="jobProgress"
            color="positive"
            size="20px"
            class="q-mb-sm"
          >
            <div class="absolute-full flex flex-center">
              <q-badge
                color="white"
                text-color="primary"
                :label="`${progressInfo.percentage.toFixed(1)}%`"
              />
            </div>
          </q-linear-progress>

          <!-- Progress details grid -->
          <div class="progress-stats q-mt-sm">
            <div class="stat-item">
              <div class="stat-label">Points</div>
              <div class="stat-value">{{ pointsFormatted }}</div>
            </div>

            <div class="stat-item" v-if="speedFormatted">
              <div class="stat-label">Speed</div>
              <div class="stat-value">{{ speedFormatted }}</div>
            </div>

            <div class="stat-item highlight" v-if="etaFormatted">
              <div class="stat-label">ETA</div>
              <div class="stat-value">{{ etaFormatted }}</div>
            </div>

            <div class="stat-item" v-if="completionTimeFormatted">
              <div class="stat-label">Complete at</div>
              <div class="stat-value">{{ completionTimeFormatted }}</div>
            </div>
          </div>
        </div>

        <q-btn
          v-if="jobStatus === 'Complete' || jobStatus === 'SuccessCriteriaMet'"
          label="Download File"
          outline
          color="positive"
          class="q-mt-md full-width"
          @click="downloadResult"
          icon="download"
        />

        <q-btn
          v-else-if="jobStatus !== 'Error'"
          label="Check Status"
          color="secondary"
          outline
          class="q-mt-md full-width"
          @click="checkJobStatus"
          :loading="checkingStatus"
          icon="refresh"
        />
      </div>

      <!-- Status log (can be expanded/collapsed) -->
      <div v-if="statusLogs.length" class="q-mt-md">
        <q-expansion-item
          label="Status Log"
          header-class="text-primary"
          icon="list"
        >
          <q-card>
            <q-card-section class="status-log q-pa-sm">
              <div
                v-for="(log, index) in statusLogs"
                :key="index"
                class="log-item"
              >
                <span class="text-caption">{{ log.time }}:</span>
                {{ log.message }}
              </div>
            </q-card-section>
          </q-card>
        </q-expansion-item>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { ref, onBeforeUnmount, onMounted, computed } from "vue";
import ClipVolume from "@/components/ClipVolume.vue";
import { formatOptions, epsgOptions, type SelectOption } from "@/utils/api";
import useDownloadService from "@/utils/useDownloadService";
import type { JobParams } from "@/utils/useDownloadService";
import { usePointCloudStore } from "@/stores/pointcloud";
import { useDirectoryStore } from "@/stores/directoryStore";

const store = usePointCloudStore();
const directoryStore = useDirectoryStore();

// Keep the entire service instance available
const downloadService = useDownloadService();

// Extract frequently used properties
const {
  processing,
  currentJob,
  closeConnection,
  jobStatus,
  jobProgress,
  progressInfo,
  statusLogs,
  startJob,
  downloadResult,
  checkJobStatus,
  checkingStatus,
} = downloadService;

const { clipPosition, clipRotation, clipScale } = store;

// Format ETA seconds as human-readable string
const etaFormatted = computed(() => {
  if (!progressInfo.value?.eta_seconds) return null;

  const seconds = progressInfo.value.eta_seconds;
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = Math.floor(seconds % 60);

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  } else {
    return `${secs}s`;
  }
});

// Format processing speed
const speedFormatted = computed(() => {
  if (!progressInfo.value?.points_per_second) return null;

  const speed = progressInfo.value.points_per_second;

  if (speed > 1000000) {
    return `${(speed / 1000000).toFixed(2)}M pts/s`;
  } else if (speed > 1000) {
    return `${(speed / 1000).toFixed(2)}K pts/s`;
  } else {
    return `${speed.toFixed(0)} pts/s`;
  }
});

// Format completion time
const completionTimeFormatted = computed(() => {
  if (!progressInfo.value?.estimated_completion_time) return null;

  const date = new Date(progressInfo.value.estimated_completion_time);
  return date.toLocaleTimeString();
});

// Format processed/total points
const pointsFormatted = computed(() => {
  if (!progressInfo.value) return null;

  const { processed, total } = progressInfo.value;
  return `${processed.toLocaleString()} / ${total.toLocaleString()}`;
});

// Form values
const type = ref("traj");
const format = ref<SelectOption | undefined>(undefined);
const epsg = ref<string | undefined>(undefined);
const density = ref("");
const number = ref(1000);

// Store the file path, defaulting to the standard path
const filePath = ref("");

onMounted(() => {
  if (
    directoryStore.activeMission &&
    directoryStore.missionData &&
    directoryStore.missionData.metacloud_filename
  ) {
    // Construct the full path using the active mission from directory store
    const missionKey = directoryStore.activeMission;
    const metacloudFilename = directoryStore.missionData.metacloud_filename;
    filePath.value = `/LiDAR/${missionKey}/${metacloudFilename}`;
  } else {
    // Use the default path
    console.error(
      "No metacloud_filename found in mission data.",
      directoryStore.missionData,
    );
  }

  console.log("Using file path:", filePath.value);
});

// Function to handle form submission
function onSubmit(): void {
  // Create params object from form values
  const params: JobParams = {
    file_path: filePath.value, // Use the stored file path
    format: format.value ? format.value.value : undefined,
    number: parseInt(number.value as any),
  };

  // Add optional parameters if they exist
  if (epsg.value) params.outcrs = epsg.value;
  if (density.value) params.density = density.value;

  if (store.clipVolume) {
    // ROI format: x0,y0,z0,dx,dy,dz,rx,ry,rz
    // where x0,y0,z0 is position, dx,dy,dz is dimensions (scale), rx,ry,rz is rotation in radians
    params.roi = [
      clipPosition.x,
      clipPosition.y,
      clipPosition.z,
      clipScale.x,
      clipScale.y,
      clipScale.z,
      clipRotation.x,
      clipRotation.y,
      clipRotation.z,
    ];
    console.log("ROI parameters:", {
      position: [clipPosition.x, clipPosition.y, clipPosition.z],
      scale: [clipScale.x, clipScale.y, clipScale.z],
      rotation_rad: [clipRotation.x, clipRotation.y, clipRotation.z],
      rotation_deg: [
        (clipRotation.x * 180) / Math.PI,
        (clipRotation.y * 180) / Math.PI,
        (clipRotation.z * 180) / Math.PI,
      ],
      roi_array: params.roi,
    });
  }
  // If type is metadata, add special flag
  if (type.value === "metadata") params.remove_all_attributes = true;

  // Call the startJob function with our params
  startJob(params);
}

// Clean up WebSocket connection when component is destroyed
onBeforeUnmount(closeConnection);
</script>

<style scoped>
.status-log {
  max-height: 200px;
  overflow-y: auto;
  background-color: #f5f5f5;
  font-family: monospace;
  font-size: 0.8rem;
}

.log-item {
  padding: 2px 0;
  border-bottom: 1px solid #eee;
}

.log-item:last-child {
  border-bottom: none;
}

.full-width {
  width: 100%;
}

/* Progress stats styling */
.progress-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 0.75rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.5rem;
  border-radius: 4px;
  background: #f9f9f9;
}

.stat-item.highlight {
  background: #fff3e0;
  border: 1px solid #ffb74d;
}

.stat-label {
  font-size: 0.7rem;
  color: #666;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 0.95rem;
  color: #333;
  font-weight: 600;
}
</style>
