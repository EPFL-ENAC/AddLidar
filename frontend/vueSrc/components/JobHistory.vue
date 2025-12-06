<template>
  <q-expansion-item icon="history" label="Job History">
    <q-card flat>
      <q-card-section>
        <div
          v-if="allJobs.length === 0"
          class="text-center text-grey-6 q-pa-md"
        >
          No jobs yet
        </div>

        <q-list v-else separator>
          <q-item
            v-for="job in allJobs"
            :key="job.job_name"
            clickable
            @click="selectJob(job.job_name)"
            :active="currentJobName === job.job_name"
          >
            <q-item-section>
              <q-item-label>
                {{ job.job_name }}
                <q-chip
                  :color="getStatusColor(job.status)"
                  text-color="white"
                  size="sm"
                  class="q-ml-sm"
                >
                  {{ job.status }}
                </q-chip>
              </q-item-label>
              <q-item-label caption>
                {{ formatDate(job.created_at) }}
              </q-item-label>
            </q-item-section>

            <q-item-section side>
              <div class="row q-gutter-xs">
                <q-btn
                  v-if="
                    job.status === 'Complete' ||
                    job.status === 'SuccessCriteriaMet'
                  "
                  flat
                  round
                  dense
                  icon="download"
                  color="positive"
                  size="sm"
                  @click.stop="downloadJob(job.job_name)"
                >
                  <q-tooltip>Download</q-tooltip>
                </q-btn>
                <q-btn
                  flat
                  round
                  dense
                  icon="delete"
                  color="negative"
                  size="sm"
                  @click.stop="removeJob(job.job_name)"
                >
                  <q-tooltip>Remove from history</q-tooltip>
                </q-btn>
              </div>
            </q-item-section>
          </q-item>
        </q-list>

        <div v-if="allJobs.length > 0" class="q-mt-md">
          <q-btn
            flat
            label="Clear All History"
            color="negative"
            size="sm"
            icon="delete_sweep"
            class="full-width"
            @click="confirmClearAll"
          />
        </div>
      </q-card-section>
    </q-card>
  </q-expansion-item>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useJobStore } from "@/stores/jobStore";
import { useQuasar } from "quasar";

const $q = useQuasar();
const jobStore = useJobStore();

const allJobs = computed(() => jobStore.jobs);
const currentJobName = computed(() => jobStore.currentJobName);

function getStatusColor(status: string): string {
  if (status === "Complete" || status === "SuccessCriteriaMet") {
    return "positive";
  } else if (
    status === "Error" ||
    status === "Failed" ||
    status === "FailureTarget"
  ) {
    return "negative";
  } else if (status === "Running" || status === "Started") {
    return "primary";
  }
  return "grey";
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins} min ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;

  return date.toLocaleDateString();
}

function selectJob(jobName: string) {
  // Just set it as the current job in the store
  // ExportRequestPanel will pick it up via watch
  jobStore.setCurrentJob(jobName);
}

async function downloadJob(jobName: string) {
  // Set as current job and let ExportRequestPanel handle it
  jobStore.setCurrentJob(jobName);

  // Navigate to or expand the download panel
  // The download will be available there
}

function removeJob(jobName: string) {
  $q.dialog({
    title: "Confirm",
    message: `Remove job ${jobName} from history?`,
    cancel: true,
    persistent: false,
  }).onOk(() => {
    jobStore.removeJob(jobName);
  });
}

function confirmClearAll() {
  $q.dialog({
    title: "Confirm",
    message: "Clear all job history? This cannot be undone.",
    cancel: true,
    persistent: false,
  }).onOk(() => {
    jobStore.clearAllJobs();
  });
}
</script>
