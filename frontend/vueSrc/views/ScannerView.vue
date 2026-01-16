<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useQuasar } from "quasar";
import { useScannerStore } from "@/stores/scannerStore";
import { useKeycloak } from "@/composables/useKeycloak";
import MainAppLayout from "@/layouts/MainAppLayout.vue";
import { useAppMeta } from "@/composables/useMeta";

useAppMeta({ title: "Scanner Management" });

const $q = useQuasar();
const scannerStore = useScannerStore();
const { login, userProfile, init } = useKeycloak();

const selectedJobType = ref<string>("all");
const showJobDetails = ref(false);
const selectedJob = ref<string | null>(null);
const autoRefresh = ref(false);
const refreshInterval = ref<number | null>(null);
const isInitializing = ref(true);

const jobTypeOptions = [
  { label: "All Jobs", value: "all" },
  { label: "Scanner", value: "scanner" },
  { label: "Compression", value: "compression" },
  { label: "Potree Conversion", value: "potree-conversion" },
];

const statusColor = (status: string) => {
  switch (status.toLowerCase()) {
    case "running":
    case "pending":
      return "primary";
    case "succeeded":
    case "complete":
      return "positive";
    case "failed":
      return "negative";
    default:
      return "grey";
  }
};

const statusIcon = (status: string) => {
  switch (status.toLowerCase()) {
    case "running":
      return "play_circle";
    case "pending":
      return "schedule";
    case "succeeded":
    case "complete":
      return "check_circle";
    case "failed":
      return "error";
    default:
      return "help";
  }
};

async function handleTriggerScanner() {
  try {
    await scannerStore.triggerScanner();
    $q.notify({
      type: "positive",
      message: "Scanner triggered successfully",
      position: "top",
    });
  } catch (error) {
    $q.notify({
      type: "negative",
      message: scannerStore.error || "Failed to trigger scanner",
      position: "top",
    });
  }
}

async function refreshData() {
  try {
    await Promise.all([
      scannerStore.fetchStatus(),
      scannerStore.fetchJobs(
        selectedJobType.value === "all" ? undefined : selectedJobType.value,
      ),
    ]);
  } catch (error) {
    console.error("Error refreshing data:", error);
  }
}

async function viewJobDetails(jobName: string) {
  selectedJob.value = jobName;
  showJobDetails.value = true;
  try {
    await Promise.all([
      scannerStore.fetchJobDetails(jobName),
      scannerStore.fetchJobLogs(jobName),
    ]);
  } catch (error) {
    $q.notify({
      type: "negative",
      message: "Failed to load job details",
      position: "top",
    });
  }
}

function closeJobDetails() {
  showJobDetails.value = false;
  selectedJob.value = null;
  scannerStore.clearSelectedJob();
}

function toggleAutoRefresh() {
  if (autoRefresh.value) {
    refreshInterval.value = window.setInterval(refreshData, 10000); // 10 seconds
  } else if (refreshInterval.value !== null) {
    clearInterval(refreshInterval.value);
    refreshInterval.value = null;
  }
}

onMounted(async () => {
  try {
    // Initialize Keycloak first
    const { init: initKeycloak, isAuthenticated: authStatus } = useKeycloak();
    await initKeycloak();

    // Update initialization status
    isInitializing.value = false;

    // Check if authenticated
    if (!authStatus.value) {
      await login();
      return;
    }

    // Load data
    await refreshData();
  } catch (error) {
    console.error("Initialization error:", error);
    isInitializing.value = false;
  }
});
</script>

<template>
  <MainAppLayout>
    <template #content>
      <!-- Loading state during Keycloak initialization -->
      <div
        v-if="isInitializing"
        class="full-width full-height flex flex-center"
      >
        <q-spinner-dots size="50px" color="primary" />
        <div class="q-mt-md text-grey-6">Initializing authentication...</div>
      </div>

      <!-- Main content after initialization -->
      <div v-else class="scanner-management q-pa-md">
        <!-- Header -->
        <div class="row items-center q-mb-md">
          <div class="col">
            <h4 class="q-my-none">Scanner Management</h4>
            <p class="text-grey-6 q-mb-none">
              Manage and monitor LiDAR scanner jobs
            </p>
          </div>
          <div class="col-auto">
            <q-chip
              v-if="userProfile"
              icon="person"
              color="primary"
              text-color="white"
            >
              {{ userProfile.username }}
            </q-chip>
          </div>
        </div>

        <!-- Status Card -->
        <q-card class="q-mb-md">
          <q-card-section class="row items-center">
            <div class="col">
              <div class="text-h6">Scanner Status</div>
              <div class="text-caption text-grey-6">
                Current scanner state and active jobs
              </div>
            </div>
            <div class="col-auto">
              <q-chip
                :color="scannerStore.isRunning ? 'positive' : 'grey'"
                text-color="white"
                :icon="scannerStore.isRunning ? 'play_circle' : 'stop_circle'"
              >
                {{ scannerStore.isRunning ? "Running" : "Idle" }}
              </q-chip>
            </div>
          </q-card-section>

          <q-separator />

          <q-card-section class="row q-gutter-md">
            <q-btn
              color="primary"
              icon="play_arrow"
              label="Trigger Scanner"
              :loading="scannerStore.loading"
              :disable="scannerStore.isRunning"
              @click="handleTriggerScanner"
            />
            <q-btn
              color="secondary"
              icon="refresh"
              label="Refresh"
              :loading="scannerStore.loading"
              @click="refreshData"
            />
            <q-toggle
              v-model="autoRefresh"
              label="Auto-refresh (10s)"
              @update:model-value="toggleAutoRefresh"
            />
          </q-card-section>
        </q-card>

        <!-- Jobs List -->
        <q-card>
          <q-card-section class="row items-center">
            <div class="col">
              <div class="text-h6">Jobs</div>
            </div>
            <div class="col-auto">
              <q-select
                v-model="selectedJobType"
                :options="jobTypeOptions"
                option-label="label"
                option-value="value"
                emit-value
                map-options
                dense
                outlined
                style="min-width: 150px"
                @update:model-value="refreshData"
              />
            </div>
          </q-card-section>

          <q-separator />

          <q-list separator>
            <q-item
              v-for="job in scannerStore.jobs"
              :key="job.name"
              clickable
              @click="viewJobDetails(job.name)"
            >
              <q-item-section avatar>
                <q-icon
                  :name="statusIcon(job.status)"
                  :color="statusColor(job.status)"
                  size="md"
                />
              </q-item-section>

              <q-item-section>
                <q-item-label>{{ job.name }}</q-item-label>
                <q-item-label caption>
                  Type: {{ job.type }} | Created:
                  {{ new Date(job.created_at).toLocaleString() }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <q-chip
                  :color="statusColor(job.status)"
                  text-color="white"
                  size="sm"
                >
                  {{ job.status }}
                </q-chip>
              </q-item-section>
            </q-item>

            <q-item v-if="!scannerStore.hasJobs && !scannerStore.loading">
              <q-item-section class="text-center text-grey-6">
                No jobs found
              </q-item-section>
            </q-item>
          </q-list>

          <q-inner-loading :showing="scannerStore.loading">
            <q-spinner-dots size="50px" color="primary" />
          </q-inner-loading>
        </q-card>

        <!-- Job Details Dialog -->
        <q-dialog v-model="showJobDetails" @hide="closeJobDetails">
          <q-card style="min-width: 600px; max-width: 800px">
            <q-card-section class="row items-center q-pb-none">
              <div class="text-h6">Job Details</div>
              <q-space />
              <q-btn icon="close" flat round dense v-close-popup />
            </q-card-section>

            <q-separator />

            <q-card-section v-if="scannerStore.selectedJob">
              <div class="q-gutter-sm">
                <div>
                  <strong>Name:</strong> {{ scannerStore.selectedJob.name }}
                </div>
                <div>
                  <strong>Status:</strong>
                  <q-chip
                    :color="statusColor(scannerStore.selectedJob.status)"
                    text-color="white"
                    size="sm"
                  >
                    {{ scannerStore.selectedJob.status }}
                  </q-chip>
                </div>
                <div>
                  <strong>Type:</strong> {{ scannerStore.selectedJob.type }}
                </div>
                <div>
                  <strong>Created:</strong>
                  {{
                    new Date(
                      scannerStore.selectedJob.created_at,
                    ).toLocaleString()
                  }}
                </div>
                <div v-if="scannerStore.selectedJob.completed_at">
                  <strong>Completed:</strong>
                  {{
                    new Date(
                      scannerStore.selectedJob.completed_at,
                    ).toLocaleString()
                  }}
                </div>
                <div v-if="scannerStore.selectedJob.duration">
                  <strong>Duration:</strong>
                  {{ scannerStore.selectedJob.duration }}
                </div>
              </div>
            </q-card-section>

            <q-separator />

            <q-card-section>
              <div class="text-subtitle1 q-mb-sm">Logs</div>
              <div
                v-for="(log, podName) in scannerStore.selectedJobLogs"
                :key="podName"
                class="q-mb-md"
              >
                <div class="text-caption text-grey-7 q-mb-xs">
                  {{ podName }}
                </div>
                <q-card flat bordered>
                  <q-card-section
                    class="bg-grey-10 text-white"
                    style="
                      font-family: monospace;
                      font-size: 12px;
                      white-space: pre-wrap;
                      max-height: 300px;
                      overflow-y: auto;
                    "
                  >
                    {{ log }}
                  </q-card-section>
                </q-card>
              </div>
              <div
                v-if="Object.keys(scannerStore.selectedJobLogs).length === 0"
                class="text-grey-6 text-center"
              >
                No logs available
              </div>
            </q-card-section>
          </q-card>
        </q-dialog>
      </div>
    </template>
  </MainAppLayout>
</template>

<style scoped lang="scss">
.scanner-management {
  max-width: 1200px;
  margin: 0 auto;
}
</style>
