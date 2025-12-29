<script setup lang="ts">
import { computed } from "vue";
import { useJobStore } from "@/stores/jobStore";
import { useQuasar } from "quasar";
import { formatJobName } from "@/utils/formatJobName";

const $q = useQuasar();
const jobStore = useJobStore();

const allJobs = computed(() => jobStore.jobs);
const currentJobName = computed(() => jobStore.currentJobName);

function getStatusColor(status: string): string {
  if (status === "Complete" || status === "SuccessCriteriaMet")
    return "positive";
  if (["Error", "Failed", "FailureTarget"].includes(status)) return "negative";
  if (status === "Running" || status === "Started") return "primary";
  return "grey";
}

function getStatusIcon(status: string): string {
  if (status === "Complete" || status === "SuccessCriteriaMet")
    return "check_circle";
  if (["Error", "Failed", "FailureTarget"].includes(status)) return "error";
  if (status === "Running" || status === "Started") return "pending";
  return "help_outline";
}

function formatDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

function selectJob(jobName: string) {
  jobStore.setCurrentJob(jobName);
}

function removeJob(jobName: string) {
  $q.dialog({
    title: "Remove Export",
    message: `Remove "${jobName}" from history?`,
    cancel: true,
  }).onOk(() => jobStore.removeJob(jobName));
}

function clearAll() {
  $q.dialog({
    title: "Clear History",
    message: "Remove all exports from history?",
    cancel: true,
  }).onOk(() => jobStore.clearAllJobs());
}
</script>

<template>
  <!-- Empty State -->
  <div v-if="!allJobs.length" class="empty-state">
    <q-icon name="history" class="empty-state__icon" />
    <div class="empty-state__title">No exports yet</div>
    <div class="empty-state__description">Export requests will appear here</div>
  </div>

  <!-- Job Cards -->
  <div v-else class="jobs-container q-my-lg">
    <q-card
      v-for="job in allJobs"
      :key="job.job_name"
      flat
      bordered
      :class="[
        'job-card q-mx-lg',
        { 'job-card--active': currentJobName === job.job_name },
      ]"
      @click="selectJob(job.job_name)"
    >
      <q-card-section class="q-pa-sm">
        <div class="row items-center q-gutter-sm">
          <q-icon
            :name="getStatusIcon(job.status)"
            :color="getStatusColor(job.status)"
            size="sm"
          />
          <div class="col">
            <div class="text-body2 text-weight-medium ellipsis">
              {{ formatJobName(job.job_name) }}
            </div>
            <div class="text-caption text-grey-6">
              {{ formatDate(job.created_at) }}
            </div>
          </div>
          <q-chip
            :color="getStatusColor(job.status)"
            text-color="white"
            size="sm"
            dense
          >
            {{ job.status }}
          </q-chip>
          <q-btn
            flat
            round
            dense
            icon="delete_outline"
            size="sm"
            color="grey-6"
            @click.stop="removeJob(job.job_name)"
          >
            <q-tooltip>Remove</q-tooltip>
          </q-btn>
        </div>
      </q-card-section>
    </q-card>

    <q-btn
      flat
      dense
      color="negative"
      label="Clear All"
      icon="delete_sweep"
      class="full-width q-mt-sm"
      size="sm"
      @click="clearAll"
    />
  </div>
</template>

<style scoped>
.jobs-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.job-card {
  cursor: pointer;
}

.job-card:hover {
  border-left: 3px solid black;
}

.job-card--active {
  border-left: 3px solid var(--q-primary);
  background: var(--q-surface);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
  text-align: center;
}

.empty-state__icon {
  font-size: 48px;
  color: #bdbdbd;
  margin-bottom: 12px;
}

.empty-state__title {
  font-size: 16px;
  font-weight: 500;
  color: #757575;
  margin-bottom: 4px;
}

.empty-state__description {
  font-size: 14px;
  color: #9e9e9e;
}
</style>
