<script setup lang="ts">
import { ref, computed, watch, onBeforeUnmount, onMounted } from "vue";
import ClipVolume from "@/components/pointcloud/ClipVolume.vue";
import { formatOptions, epsgOptions, type SelectOption } from "@/utils/api";
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
    <!-- Restored Banner -->
    <q-banner v-if="parametersRestored" class="bg-blue-1 text-blue-9" dense>
      <template #avatar>
        <q-icon name="info" color="primary" />
      </template>
      Restored from {{ currentJob?.job_name }}
    </q-banner>

    <!-- Form Fields -->
    <div class="form-section">
      <q-select
        v-model="format"
        :options="formatOptions"
        label="Output Format"
        dense
        outlined
        class="q-mb-md"
      />

      <q-select
        v-model="epsg"
        :options="epsgOptions"
        label="Coordinate System (EPSG)"
        dense
        outlined
        clearable
        class="q-mb-md"
      />

      <q-input
        v-model.number="maxPoints"
        type="number"
        label="Max Points"
        dense
        outlined
        class="q-mb-md"
      />

      <clip-volume />
    </div>

    <!-- Submit Button -->
    <div class="form-section">
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
      <q-separator />

      <div class="form-section">
        <div class="section-header">
          <span class="section-header__title">Current Job</span>
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
          {{ currentJob.job_name }}
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
  </q-form>
</template>

<style scoped>
.log-container {
  max-height: 200px;
  overflow-y: auto;
  background: #f8fafc;
  border-radius: 4px;
  padding: 8px;
  font-family: monospace;
  font-size: 11px;
}
</style>
