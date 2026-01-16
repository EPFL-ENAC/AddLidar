/**
 * Scanner Store
 *
 * Manages scanner job state, triggering, and monitoring.
 */

import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { useKeycloak } from "@/composables/useKeycloak";

export interface ScannerJob {
  name: string;
  status: string;
  type: string;
  created_at: string;
  completed_at?: string;
  duration?: string;
}

export interface ScannerStatus {
  is_running: boolean;
  running_jobs: ScannerJob[];
  total_scanner_jobs: number;
}

export interface JobDetails extends ScannerJob {
  namespace?: string;
  image?: string;
  active_pods?: number;
  succeeded_pods?: number;
  failed_pods?: number;
}

export interface JobLogs {
  [podName: string]: string;
}

const API_BASE = "/api/scanner";

export const useScannerStore = defineStore("scanner", () => {
  const { authHeader, updateToken } = useKeycloak();

  const status = ref<ScannerStatus | null>(null);
  const jobs = ref<ScannerJob[]>([]);
  const selectedJob = ref<JobDetails | null>(null);
  const selectedJobLogs = ref<JobLogs>({});
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isRunning = computed(() => status.value?.is_running ?? false);
  const hasJobs = computed(() => jobs.value.length > 0);

  /**
   * Trigger a new scanner job
   */
  async function triggerScanner() {
    loading.value = true;
    error.value = null;

    try {
      await updateToken();

      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };
      if (authHeader.value) {
        Object.assign(headers, authHeader.value);
      }

      const response = await fetch(`${API_BASE}/trigger`, {
        method: "POST",
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to trigger scanner: ${response.statusText}`);
      }

      const data = await response.json();

      // Refresh status after triggering
      await fetchStatus();

      return data;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Unknown error";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch scanner status
   */
  async function fetchStatus() {
    loading.value = true;
    error.value = null;

    try {
      await updateToken();

      const headers: HeadersInit = {};
      if (authHeader.value) {
        Object.assign(headers, authHeader.value);
      }

      const response = await fetch(`${API_BASE}/status`, {
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch status: ${response.statusText}`);
      }

      status.value = await response.json();
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Unknown error";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch list of jobs
   */
  async function fetchJobs(jobType?: string, limit = 50) {
    loading.value = true;
    error.value = null;

    try {
      await updateToken();

      const params = new URLSearchParams();
      if (jobType) params.append("job_type", jobType);
      params.append("limit", limit.toString());

      const headers: HeadersInit = {};
      if (authHeader.value) {
        Object.assign(headers, authHeader.value);
      }

      const response = await fetch(`${API_BASE}/jobs?${params}`, {
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.statusText}`);
      }

      const data = await response.json();
      jobs.value = data.jobs || [];
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Unknown error";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch job details
   */
  async function fetchJobDetails(jobName: string) {
    loading.value = true;
    error.value = null;

    try {
      await updateToken();

      const headers: HeadersInit = {};
      if (authHeader.value) {
        Object.assign(headers, authHeader.value);
      }

      const response = await fetch(`${API_BASE}/jobs/${jobName}`, {
        headers,
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch job details: ${response.statusText}`);
      }

      const data = await response.json();
      selectedJob.value = data.job;
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Unknown error";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Fetch job logs
   */
  async function fetchJobLogs(jobName: string, tailLines = 100) {
    loading.value = true;
    error.value = null;

    try {
      await updateToken();

      const headers: HeadersInit = {};
      if (authHeader.value) {
        Object.assign(headers, authHeader.value);
      }

      const response = await fetch(
        `${API_BASE}/jobs/${jobName}/logs?tail_lines=${tailLines}`,
        {
          headers,
        },
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch job logs: ${response.statusText}`);
      }

      const data = await response.json();
      selectedJobLogs.value = data.logs || {};
    } catch (err) {
      error.value = err instanceof Error ? err.message : "Unknown error";
      throw err;
    } finally {
      loading.value = false;
    }
  }

  /**
   * Clear selected job
   */
  function clearSelectedJob() {
    selectedJob.value = null;
    selectedJobLogs.value = {};
  }

  /**
   * Clear error
   */
  function clearError() {
    error.value = null;
  }

  return {
    // State
    status,
    jobs,
    selectedJob,
    selectedJobLogs,
    loading,
    error,

    // Computed
    isRunning,
    hasJobs,

    // Actions
    triggerScanner,
    fetchStatus,
    fetchJobs,
    fetchJobDetails,
    fetchJobLogs,
    clearSelectedJob,
    clearError,
  };
});
