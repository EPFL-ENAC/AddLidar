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
              <q-item v-for="(log, index) in statusLogs" :key="index">
                <q-item-section>
                  <q-item-label caption>{{ log.time }}</q-item-label>
                  <q-item-label>{{ log.message }}</q-item-label>
                </q-item-section>
              </q-item>
            </q-list>
          </q-expansion-item>
        </div>
      </q-card-section>
    </q-card>
  </q-expansion-item>
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
}
</style>
