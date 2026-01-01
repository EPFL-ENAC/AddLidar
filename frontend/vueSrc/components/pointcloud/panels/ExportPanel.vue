<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount, onMounted } from "vue";
import ClipVolume from "@/components/pointcloud/ClipVolume.vue";
import JobsPanel from "@/components/pointcloud/panels/JobsPanel.vue";
import { formatOptions, epsgOptions, type SelectOption } from "@/utils/api";
import { formatJobName } from "@/utils/formatJobName";
import useDownloadService from "@/utils/useDownloadService";
import type { JobParams } from "@/utils/useDownloadService";
import { useExportJobStore } from "@/stores/exportJobStore";
import { useDirectoryStore } from "@/stores/directoryStore";
import { useJobStore } from "@/stores/jobStore";

const exportJobStore = useExportJobStore();
const directoryStore = useDirectoryStore();
const jobStore = useJobStore();

const downloadService = useDownloadService();
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
  loadJob,
  getLoadedJobParams,
  isLoadingFromHistory,
} = downloadService;

const { clipPosition, clipRotation, clipScale } = exportJobStore;

// Form state
const format = ref<SelectOption | undefined>(undefined);
const epsg = ref<string | undefined>(undefined);
const maxPoints = ref(1000);
const density = ref<number | undefined>(undefined);
const removeColor = ref(false);
const removeAllAttributes = ref(false);
const lineIndex = ref<number | undefined>(undefined);
const maxReturns = ref<number | undefined>(undefined);
const parametersRestored = ref(false);
const showLogs = ref(false);

const filePath = computed(() => {
  if (
    directoryStore.activeMission &&
    directoryStore.missionData?.metacloud_filename
  ) {
    return `/LiDAR/${directoryStore.activeMission}/${directoryStore.missionData.metacloud_filename}`;
  }
  return "";
});

const isComplete = computed(() =>
  ["Complete", "SuccessCriteriaMet"].includes(jobStatus.value),
);

const isError = computed(() =>
  ["Error", "Failed", "FailureTarget"].includes(jobStatus.value),
);

const isRunning = computed(() =>
  ["Running", "Started"].includes(jobStatus.value),
);

const progressPercent = computed(
  () =>
    progressInfo.value?.percentage?.toFixed(0) ??
    Math.floor(jobProgress.value * 100),
);

function onSubmit() {
  parametersRestored.value = false;

  const params: JobParams = {
    file_path: filePath.value,
    format: format.value?.value,
    number: maxPoints.value,
  };

  if (epsg.value) params.outcrs = epsg.value;
  if (density.value !== undefined) params.density = density.value;
  if (removeColor.value) params.remove_color = true;
  if (removeAllAttributes.value) params.remove_all_attributes = true;
  if (lineIndex.value !== undefined) params.line = lineIndex.value;
  if (maxReturns.value !== undefined) params.returns = maxReturns.value;

  if (exportJobStore.clipVolume) {
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
  }

  startJob(params);
}

function restoreJobParameters() {
  const params = getLoadedJobParams();
  if (!params) return;

  parametersRestored.value = true;

  if (params.format) {
    format.value = formatOptions.find((opt) => opt.value === params.format);
  }
  if (params.outcrs) epsg.value = params.outcrs;
  if (params.number) maxPoints.value = params.number;
  if (params.density !== undefined) density.value = params.density as number;
  if (params.remove_color) removeColor.value = params.remove_color;
  if (params.remove_all_attributes)
    removeAllAttributes.value = params.remove_all_attributes;
  if (params.line !== undefined) lineIndex.value = params.line;
  if (params.returns !== undefined) maxReturns.value = params.returns;

  if (params.roi?.length === 9) {
    const [x, y, z, sx, sy, sz, rx, ry, rz] = params.roi;
    exportJobStore.setClipPosition({ x, y, z });
    exportJobStore.setClipScale({ x: sx, y: sy, z: sz });
    exportJobStore.setClipRotation({ x: rx, y: ry, z: rz });
  }
}

watch(isLoadingFromHistory, (isLoading) => {
  if (isLoading && currentJob.value) {
    restoreJobParameters();
    isLoadingFromHistory.value = false;
  }
});

watch(
  () => jobStore.currentJobName,
  (newJobName) => {
    if (newJobName && newJobName !== currentJob.value?.job_name) {
      loadJob(newJobName);
    }
  },
);

onMounted(() => {
  if (jobStore.currentJobName) loadJob(jobStore.currentJobName);
});

onBeforeUnmount(closeConnection);
</script>

<template>
  <q-form @submit.prevent="onSubmit">
    <!-- Form Fields -->
    <div>
      <!-- Output Settings -->
      <q-expansion-item
        label="Output Settings"
        icon="settings"
        header-class="text-grey-8"
        :default-opened="true"
      >
        <div class="q-pt-sm">
          <q-select
            v-model="format"
            :options="formatOptions"
            label="Output Format"
            hint="File format for exported point cloud"
            dense
            outlined
            class="q-mb-md"
          />

          <q-select
            v-model="epsg"
            :options="epsgOptions"
            label="Output Coordinate System"
            hint="Transform to this CRS (e.g., EPSG:4326). Leave empty for no transformation"
            dense
            outlined
            clearable
            class="q-mb-md"
          />
        </div>
      </q-expansion-item>

      <!-- Sampling & Filtering -->
      <q-expansion-item
        label="Sampling & Filtering"
        icon="filter_alt"
        header-class="text-grey-8"
      >
        <div class="q-pt-sm">
          <q-input
            v-model.number="maxPoints"
            type="number"
            label="Max Points"
            hint="Maximum number of points in output. Points will be spread uniformly"
            dense
            outlined
            class="q-mb-md"
          />

          <q-input
            v-model.number="density"
            type="number"
            label="Max Density (pts/m²)"
            hint="Maximum point density in points per square meter"
            dense
            outlined
            clearable
            class="q-mb-md"
            :min="0"
            step="0.1"
          />

          <q-input
            v-model.number="lineIndex"
            type="number"
            label="Line Index"
            hint="Export only a specific line index from the scan"
            dense
            outlined
            clearable
            class="q-mb-md"
            :min="0"
          />

          <q-input
            v-model.number="maxReturns"
            type="number"
            label="Max Return Index"
            hint="Maximum return index to include (use -1 for no limit)"
            dense
            outlined
            clearable
            class="q-mb-md"
            :min="-1"
          />
        </div>
      </q-expansion-item>

      <!-- Attribute Filtering -->
      <q-expansion-item
        label="Attribute Filtering"
        icon="tune"
        header-class="text-grey-8"
      >
        <div class="q-pt-sm">
          <q-checkbox
            v-model="removeColor"
            label="Remove Color Data"
            dense
            class="q-mb-sm"
          >
            <q-tooltip
              >Remove RGB color information from the point cloud</q-tooltip
            >
          </q-checkbox>

          <q-checkbox
            v-model="removeAllAttributes"
            label="Remove All Attributes"
            dense
            class="q-mb-md"
          >
            <q-tooltip
              >Keep only geometry (XYZ), remove all other attributes</q-tooltip
            >
          </q-checkbox>
        </div>
      </q-expansion-item>

      <!-- Region of Interest -->
      <q-expansion-item
        label="Region of Interest"
        icon="crop"
        header-class="text-grey-8"
      >
        <div class="q-pt-sm">
          <clip-volume />
        </div>
      </q-expansion-item>
    </div>

    <!-- Submit Button -->
    <div class="form-section row justify-center q-my-md q-mx-sm">
      <q-btn
        type="submit"
        color="primary"
        unelevated
        class="full-width"
        label="Export"
        icon="file_download"
        :loading="processing"
        :disable="processing || !filePath"
      />
    </div>

    <!-- Job Status -->
    <template v-if="currentJob">
      <div class="q-pa-md">
        <div class="section-header">
          <span class="section-header__title">Current Export</span>
          <q-chip
            :color="isComplete ? 'positive' : isError ? 'negative' : 'primary'"
            text-color="white"
            size="sm"
            :icon="isComplete ? 'check' : isError ? 'error' : 'pending'"
          >
            {{ jobStatus }}
          </q-chip>
        </div>

        <div class="text-caption text-grey-6 q-mb-sm">
          {{ formatJobName(currentJob.job_name) }}
        </div>

        <!-- Progress -->
        <template v-if="isRunning">
          <q-linear-progress
            :value="jobProgress"
            :indeterminate="jobProgress === 0"
            color="primary"
            class="q-mb-sm"
            rounded
          />
          <div v-if="progressInfo" class="text-caption text-grey-6">
            {{ progressPercent }}% complete
            <template v-if="progressInfo.points_per_second">
              · {{ (progressInfo.points_per_second / 1000000).toFixed(1) }}M
              pts/s
            </template>
          </div>
        </template>

        <!-- Actions -->
        <div class="q-mt-md q-gutter-sm">
          <q-btn
            v-if="isComplete"
            color="positive"
            unelevated
            class="full-width"
            label="Download Result"
            icon="download"
            @click="downloadResult"
          />

          <q-btn
            v-else-if="!isError && !isRunning"
            flat
            color="primary"
            class="full-width"
            label="Refresh Status"
            icon="refresh"
            :loading="checkingStatus"
            @click="checkJobStatus"
          />
        </div>

        <!-- Logs Toggle -->
        <q-btn
          v-if="statusLogs.length"
          flat
          dense
          color="grey-7"
          :icon="showLogs ? 'expand_less' : 'expand_more'"
          :label="showLogs ? 'Hide Logs' : `Show Logs (${statusLogs.length})`"
          class="full-width q-mt-sm"
          @click="showLogs = !showLogs"
        />

        <!-- Logs -->
        <q-slide-transition>
          <div v-show="showLogs" class="log-container q-mt-sm">
            <div
              v-for="(log, i) in statusLogs"
              :key="i"
              class="text-caption q-py-xs"
            >
              <span class="text-grey-5">{{ log.time }}</span>
              {{
                typeof log.message === "string"
                  ? log.message
                  : JSON.stringify(log.message)
              }}
            </div>
          </div>
        </q-slide-transition>
      </div>
    </template>

    <!-- Job History Section -->

    <div class="q-pt-lg q-pt-md">
      <q-expansion-item
        icon="history"
        label="Export History"
        header-class="text-grey-8"
      >
        <jobs-panel />
      </q-expansion-item>
    </div>
  </q-form>
</template>

<style scoped>
.log-container {
  max-height: 200px;
  max-width: 100%;
  overflow-y: auto;
  overflow-x: auto;
  background: #f8fafc;
  border-radius: 4px;
  padding: 8px;
  font-family: monospace;
  font-size: 11px;
  word-break: break-word;
  overflow-wrap: anywhere;
}
</style>
