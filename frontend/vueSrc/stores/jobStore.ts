import { defineStore } from "pinia";
import { ref, watch } from "vue";

export interface JobRecord {
  job_name: string;
  status: string;
  created_at: string;
  file_path: string;
  format?: string;
  outcrs?: string;
  number?: number;
  density?: number;
  roi?: number[];
  remove_color?: boolean;
  remove_all_attributes?: boolean;
  line?: number;
  returns?: number;
  last_updated: string;
  completed_at?: string;
  error_message?: string;
}

const STORAGE_KEY = "addlidar_jobs";
const MAX_JOBS = 50; // Keep last 50 jobs

export const useJobStore = defineStore("jobs", () => {
  const jobs = ref<JobRecord[]>([]);
  const currentJobName = ref<string | null>(null);

  // Load jobs from localStorage on init
  function loadFromStorage() {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        jobs.value = JSON.parse(stored);
      }
    } catch (error) {
      console.error("Error loading jobs from storage:", error);
      jobs.value = [];
    }
  }

  // Save jobs to localStorage
  function saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(jobs.value));
    } catch (error) {
      console.error("Error saving jobs to storage:", error);
    }
  }

  // Watch jobs array for changes and save to storage
  watch(jobs, saveToStorage, { deep: true });

  // Add or update a job
  function upsertJob(job: JobRecord) {
    const index = jobs.value.findIndex((j) => j.job_name === job.job_name);

    if (index !== -1) {
      // Update existing job
      jobs.value[index] = {
        ...jobs.value[index],
        ...job,
        last_updated: new Date().toISOString(),
      };
    } else {
      // Add new job
      jobs.value.unshift({
        ...job,
        last_updated: new Date().toISOString(),
      });

      // Limit the number of stored jobs
      if (jobs.value.length > MAX_JOBS) {
        jobs.value = jobs.value.slice(0, MAX_JOBS);
      }
    }
  }

  // Get a job by name
  function getJob(jobName: string): JobRecord | undefined {
    return jobs.value.find((j) => j.job_name === jobName);
  }

  // Update job status
  function updateJobStatus(
    jobName: string,
    status: string,
    additionalData?: Partial<JobRecord>,
  ) {
    const job = getJob(jobName);
    if (job) {
      upsertJob({
        ...job,
        status,
        ...additionalData,
        last_updated: new Date().toISOString(),
        ...(status === "Complete" || status === "SuccessCriteriaMet"
          ? { completed_at: new Date().toISOString() }
          : {}),
      });
    }
  }

  // Set the current active job
  function setCurrentJob(jobName: string | null) {
    currentJobName.value = jobName;
  }

  // Get current job record
  function getCurrentJob(): JobRecord | undefined {
    if (!currentJobName.value) return undefined;
    return getJob(currentJobName.value);
  }

  // Remove a job from the list (frontend only)
  function removeJob(jobName: string) {
    const index = jobs.value.findIndex((j) => j.job_name === jobName);
    if (index !== -1) {
      jobs.value.splice(index, 1);
    }

    // If removing the current job, clear it
    if (currentJobName.value === jobName) {
      currentJobName.value = null;
    }
  }

  // Get completed jobs
  function getCompletedJobs(): JobRecord[] {
    return jobs.value.filter(
      (j) => j.status === "Complete" || j.status === "SuccessCriteriaMet",
    );
  }

  // Get running jobs
  function getRunningJobs(): JobRecord[] {
    return jobs.value.filter(
      (j) =>
        j.status === "Running" ||
        j.status === "Started" ||
        j.status === "Pending",
    );
  }

  // Get failed jobs
  function getFailedJobs(): JobRecord[] {
    return jobs.value.filter(
      (j) =>
        j.status === "Error" ||
        j.status === "Failed" ||
        j.status === "FailureTarget",
    );
  }

  // Clear all jobs
  function clearAllJobs() {
    jobs.value = [];
    currentJobName.value = null;
  }

  // Initialize by loading from storage
  loadFromStorage();

  return {
    jobs,
    currentJobName,
    upsertJob,
    getJob,
    updateJobStatus,
    setCurrentJob,
    getCurrentJob,
    removeJob,
    getCompletedJobs,
    getRunningJobs,
    getFailedJobs,
    clearAllJobs,
  };
});
