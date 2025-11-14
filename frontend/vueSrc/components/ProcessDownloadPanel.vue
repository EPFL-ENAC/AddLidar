<template>
  <q-expansion-item icon="settings" label="Process & Download">
    <q-card flat>
      <q-card-section>
        <q-form @submit.prevent="onSubmit">
          <q-select
            outlined
            label="Output Format"
            v-model="format"
            :options="formatOptions"
            color="primary"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="description" />
            </template>
          </q-select>

          <q-select
            outlined
            label="EPSG"
            :options="epsgOptions"
            v-model="epsg"
            clearable
            color="primary"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="map" />
            </template>
          </q-select>

          <div class="q-mb-md">
            <clip-volume />
          </div>

          <q-input
            outlined
            type="number"
            label="Max Points"
            v-model.number="number"
            color="primary"
            class="q-mb-md"
          >
            <template v-slot:prepend>
              <q-icon name="format_list_numbered" />
            </template>
          </q-input>

          <q-btn
            outline
            label="Generate Request"
            type="submit"
            color="primary"
            class="full-width"
            icon="play_arrow"
            :loading="processing"
            :disable="processing"
          />
        </q-form>

        <div v-if="currentJob" class="q-mt-md">
          <q-separator class="q-my-md" />

          <div class="q-mb-sm">Job Status</div>
          <div class="q-mb-md">
            <div class="row items-center q-gutter-sm q-mb-sm">
              <q-chip
                :color="
                  jobStatus === 'Complete' || jobStatus === 'SuccessCriteriaMet'
                    ? 'positive'
                    : jobStatus === 'Error'
                      ? 'negative'
                      : 'primary'
                "
                text-color="white"
                :icon="
                  jobStatus === 'Complete' || jobStatus === 'SuccessCriteriaMet'
                    ? 'check_circle'
                    : jobStatus === 'Error'
                      ? 'error'
                      : 'pending'
                "
                size="sm"
              >
                {{ jobStatus }}
              </q-chip>
              <div class="text-grey-6">{{ currentJob.job_name }}</div>
            </div>

            <div v-if="jobStatus === 'Running' && progressInfo">
              <q-linear-progress
                :value="jobProgress"
                color="positive"
                size="20px"
                class="q-mb-sm"
              />
              <div class="text-grey-6 q-mb-sm">
                {{ progressInfo.percentage.toFixed(1) }}% -
                {{ pointsFormatted }}
                <span v-if="speedFormatted"> • {{ speedFormatted }}</span>
                <span v-if="etaFormatted"> • ETA: {{ etaFormatted }}</span>
              </div>
            </div>

            <div
              v-else-if="
                jobStatus === 'Running' ||
                jobStatus === 'Started' ||
                (jobStatus && jobProgress === 0)
              "
              class="q-mb-sm text-center q-py-md"
            >
              <q-spinner color="primary" size="40px" />
              <div class="text-grey-6 q-mt-sm">Creating job...</div>
            </div>

            <div v-else-if="jobProgress > 0" class="q-mb-sm">
              <q-linear-progress
                :value="jobProgress"
                color="primary"
                size="12px"
              />
              <div class="text-grey-6 q-mt-sm">
                {{ Math.floor(jobProgress * 100) }}%
              </div>
            </div>

            <q-btn
              v-if="
                jobStatus === 'Complete' || jobStatus === 'SuccessCriteriaMet'
              "
              outline
              label="Download"
              color="positive"
              class="full-width"
              icon="download"
              @click="downloadResult"
            />

            <q-btn
              v-else-if="jobStatus !== 'Error'"
              outline
              label="Refresh"
              color="primary"
              class="full-width"
              icon="refresh"
              :loading="checkingStatus"
              @click="checkJobStatus"
            />
          </div>

          <q-expansion-item
            v-if="statusLogs.length"
            icon="article"
            label="Status Log"
            class="q-mt-sm"
          >
            <q-list separator class="status-log">
              <q-item
                v-for="(log, index) in statusLogs"
                :key="index"
                clickable
                @click="showLogDetails(log)"
              >
                <q-item-section>
                  <q-item-label caption>{{ log.time }}</q-item-label>
                  <q-item-label class="log-message">{{
                    getLogDisplayText(log)
                  }}</q-item-label>
                </q-item-section>
                <q-item-section side v-if="isJsonLog(log)">
                  <q-icon name="info" color="grey-6" size="xs" />
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>

          <!-- JSON Details Dialog -->
          <q-dialog v-model="showDetailsDialog">
            <q-card
              style="min-width: 500px; max-width: 800px; max-height: 80vh"
            >
              <q-card-section class="row items-center q-pb-none">
                <div class="text-h6">Log Details</div>
                <q-space />
                <q-btn icon="close" flat round dense v-close-popup />
              </q-card-section>

              <q-card-section
                class="q-pt-none"
                style="max-height: calc(80vh - 120px); overflow-y: auto"
              >
                <div class="text-caption text-grey-6 q-mb-sm">
                  {{ selectedLog?.time }}
                </div>
                <pre class="json-display">{{ formatJson(selectedLog) }}</pre>
              </q-card-section>

              <q-card-actions align="right">
                <q-btn
                  flat
                  label="Copy"
                  color="primary"
                  icon="content_copy"
                  @click="copyToClipboard"
                />
                <q-btn flat label="Close" color="primary" v-close-popup />
              </q-card-actions>
            </q-card>
          </q-dialog>
        </div>
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>
<script setup lang="ts">
import { ref, onBeforeUnmount, computed } from "vue";
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
const filePath = computed(() => {
  if (
    directoryStore.activeMission &&
    directoryStore.missionData &&
    directoryStore.missionData.metacloud_filename
  ) {
    // Construct the full path using the active mission from directory store
    const missionKey = directoryStore.activeMission;
    const metacloudFilename = directoryStore.missionData.metacloud_filename;
    return `/LiDAR/${missionKey}/${metacloudFilename}`;
  } else {
    // Use the default path
    console.error(
      "No metacloud_filename found in mission data.",
      directoryStore.missionData,
      directoryStore.activeMission,
      directoryStore.missionData?.metacloud_filename,
    );
    return "";
  }
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

// Log details dialog state
const showDetailsDialog = ref(false);
const selectedLog = ref<any>(null);

// Helper function to check if a log message is JSON
function isJsonLog(log: any): boolean {
  if (typeof log.message !== "string") return false;
  const trimmed = log.message.trim();
  return trimmed.startsWith("{") || trimmed.startsWith("[");
}

// Helper function to parse and extract message from log
function getLogDisplayText(log: any): string {
  if (typeof log.message !== "string") return String(log.message);

  const trimmed = log.message.trim();
  if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
    try {
      const parsed = JSON.parse(trimmed);
      // Try to extract a meaningful message
      if (parsed.message) return parsed.message;
      if (parsed.status) {
        // Show error status prominently
        if (
          parsed.status === "Error" ||
          parsed.status === "FailureTarget" ||
          parsed.status === "Failed"
        ) {
          return `❌ ${parsed.status}${parsed.logs ? " - Click for details" : ""}`;
        }
        return `Status: ${parsed.status}`;
      }
      if (parsed.type) return `Type: ${parsed.type}`;
      return "Click to view details";
    } catch {
      return log.message;
    }
  }
  return log.message;
}

// Show log details in dialog
function showLogDetails(log: any): void {
  selectedLog.value = log;
  showDetailsDialog.value = true;
}

// Format log as pretty JSON
function formatJson(log: any): string {
  if (!log) return "";

  try {
    const trimmed = log.message.trim();
    if (trimmed.startsWith("{") || trimmed.startsWith("[")) {
      const parsed = JSON.parse(trimmed);

      // If there are logs, format them separately for better readability
      if (parsed.logs) {
        const { logs, ...rest } = parsed;
        let output = JSON.stringify(rest, null, 2);
        output += "\n\n=== Detailed Logs ===\n\n";
        output += logs;
        return output;
      }

      return JSON.stringify(parsed, null, 2);
    }
    return log.message;
  } catch {
    return log.message;
  }
}

// Copy JSON to clipboard
async function copyToClipboard(): Promise<void> {
  if (!selectedLog.value) return;

  try {
    const text = formatJson(selectedLog.value);
    await navigator.clipboard.writeText(text);
  } catch (error) {
    console.error("Failed to copy to clipboard:", error);
  }
}

// Clean up WebSocket connection when component is destroyed
onBeforeUnmount(closeConnection);
</script>

<style scoped>
.status-log {
  max-height: 200px;
  overflow-y: auto;
  overflow-x: hidden;
}

.log-message {
  word-break: break-word;
  overflow-wrap: break-word;
  white-space: pre-wrap;
  max-width: 100%;
}

.json-display {
  background-color: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: "Courier New", Courier, monospace;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}
</style>
