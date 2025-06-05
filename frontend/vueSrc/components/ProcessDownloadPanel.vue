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
import { ref, onBeforeUnmount, onMounted } from "vue";
import ClipVolume from "@/components/ClipVolume.vue";
import { formatOptions, epsgOptions, type SelectOption } from "@/utils/api";
import useDownloadService from "@/utils/useDownloadService";
import type { JobParams } from "@/utils/useDownloadService";
import { usePointCloudStore } from "@/stores/pointcloud";
import { useDirectoryStore } from "@/stores/directoryStore";
import { useRoute } from "vue-router";

const store = usePointCloudStore();
const directoryStore = useDirectoryStore();
const route = useRoute();

// Keep the entire service instance available
const downloadService = useDownloadService();

// Extract frequently used properties
const {
  processing,
  currentJob,
  closeConnection,
  jobStatus,
  jobProgress,
  statusLogs,
  startJob,
  downloadResult,
  checkJobStatus,
  checkingStatus,
} = downloadService;

const { clipPosition, clipRotation, clipScale } = store;

// Form values
const type = ref("traj");
const format = ref<SelectOption | undefined>(undefined);
const epsg = ref<string | undefined>(undefined);
const density = ref("");
const number = ref(1000);

// Store the file path, defaulting to the standard path
const filePath = ref("");

// Set up the default file path or use query parameter if available
onMounted(() => {
  // Check for filename in query parameters
  if (route.query.filename && typeof route.query.filename === "string") {
    filePath.value = route.query.filename;
  } else {
    // Use the default path
    filePath.value = `/LiDAR/0001_Mission_Root/02_LAS_PCD/all_grouped_high_veg_10th_point.las`;
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

  if (store.clipVolume)
    params.roi = [
      ...Object.values(clipPosition),
      ...Object.values(clipScale),
      ...Object.values(clipRotation),
    ];

  console.log("ROI", params.roi);
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
</style>
