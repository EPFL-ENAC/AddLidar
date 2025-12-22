<script setup lang="ts">
import { computed } from "vue";
import { useJobStore } from "@/stores/jobStore";
import { useQuasar } from "quasar";

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
    title: "Remove Job",
    message: `Remove "${jobName}" from history?`,
    cancel: true,
  }).onOk(() => jobStore.removeJob(jobName));
}

function clearAll() {
  $q.dialog({
    title: "Clear History",
    message: "Remove all jobs from history?",
    cancel: true,
  }).onOk(() => jobStore.clearAllJobs());
}
</script>

<template>
  <!-- Empty State -->
  <div v-if="!allJobs.length" class="empty-state">
    <q-icon name="history" class="empty-state__icon" />
    <div class="empty-state__title">No jobs yet</div>
    <div class="empty-state__description">Export requests will appear here</div>
  </div>

  <!-- Job List -->
  <template v-else>
    <q-list separator>
      <q-item
        v-for="job in allJobs"
        :key="job.job_name"
        clickable
        :active="currentJobName === job.job_name"
        active-class="bg-blue-1"
        @click="selectJob(job.job_name)"
      >
        <q-item-section avatar>
          <q-icon
            :name="getStatusIcon(job.status)"
            :color="getStatusColor(job.status)"
          />
        </q-item-section>

        <q-item-section>
          <q-item-label lines="1">{{ job.job_name }}</q-item-label>
          <q-item-label caption>{{ formatDate(job.created_at) }}</q-item-label>
        </q-item-section>

        <q-item-section side>
          <q-btn
            flat
            round
            dense
            icon="delete_outline"
            size="sm"
            color="grey-6"
            @click.stop="removeJob(job.job_name)"
          />
        </q-item-section>
      </q-item>
    </q-list>

    <div class="form-section">
      <q-btn
        flat
        dense
        color="negative"
        label="Clear All"
        icon="delete_sweep"
        class="full-width"
        @click="clearAll"
      />
    </div>
  </template>
</template>
