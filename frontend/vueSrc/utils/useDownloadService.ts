// WebSocket and API services for file download operations
import { ref, Ref } from "vue";
import { useJobStore } from "@/stores/jobStore";
import { useDirectoryStore } from "@/stores/directoryStore";
// Define types for job-related data
interface JobLog {
  time: string;
  message: string;
}

interface JobData {
  job_name: string;
  [key: string]: any;
}

interface ProgressInfo {
  processed: number;
  total: number;
  percentage: number;
  eta_seconds?: number;
  points_per_second?: number;
  estimated_completion_time?: string;
  elapsed_seconds?: number;
}

interface JobStatusResponse {
  status: string;
  progress?: number | ProgressInfo; // Can be either legacy number or new progress object
  message?: string;
  [key: string]: any;
}

export interface JobParams {
  file_path: string;
  format?: string;
  outcrs?: string;
  density?: number | string;
  roi?: number[];
  number?: number;
  remove_all_attributes?: boolean;
  remove_color?: boolean;
  line?: number;
  returns?: number;
  [key: string]: any;
}

// Define notification handler type
type NotificationHandler = (message: string, type: string) => void;

export default function useDownloadService(
  // Optional custom notification handler
  notifyFn?: NotificationHandler,
) {
  // Base URLs for API and WebSocket
  const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;
  const WS_BASE_URL = `${
    window.location.protocol === "https:" ? "wss:" : "ws:"
  }//${window.location.hostname}:${window.location.port}`;
  const PREFIX = "/api";

  // Get job store instance
  const jobStore = useJobStore();

  // Default notification handler if none is provided
  const notify = (message: string, type: string = "info"): void => {
    if (notifyFn) {
      notifyFn(message, type);
    } else {
      console.log(`[${type.toUpperCase()}] ${message}`);
    }
  };

  // Job status variables
  const processing: Ref<boolean> = ref(false);
  const currentJob: Ref<JobData | null> = ref(null);
  const jobStatus: Ref<string> = ref("");
  const jobProgress: Ref<number> = ref(0);
  const progressInfo: Ref<ProgressInfo | null> = ref(null);
  const statusLogs: Ref<JobLog[]> = ref([]);
  const checkingStatus: Ref<boolean> = ref(false);
  const isLoadingFromHistory: Ref<boolean> = ref(false);
  let wsConnection: WebSocket | null = null;

  // Add log message with timestamp
  function addLog(message: any): void {
    const now = new Date();
    const timeStr = now.toLocaleTimeString();
    statusLogs.value.push({
      time: timeStr,
      message:
        typeof message === "object" ? JSON.stringify(message) : String(message),
    });
  }

  // Start a new job
  async function startJob(params: JobParams): Promise<void> {
    // Reset any previous job data
    currentJob.value = null;
    jobStatus.value = "";
    jobProgress.value = 0;
    statusLogs.value = [];
    isLoadingFromHistory.value = false; // Not loading from history, creating new job

    try {
      processing.value = true;
      addLog("Starting job...");

      // Get password from directory store if available
      const directoryStore = useDirectoryStore();
      const headers: HeadersInit = {
        "Content-Type": "application/json",
      };

      const currentPassword = directoryStore.missionPassword;
      if (currentPassword) {
        headers["X-Mission-Password"] = currentPassword;
      }

      const response = await fetch(`${API_BASE_URL}${PREFIX}/start-job/`, {
        method: "POST",
        headers,
        body: JSON.stringify(params),
      });

      const data = await response.json();
      processing.value = false;

      // Check if response has error (bad status code)
      if (!response.ok) {
        // Handle error response
        const errorMessage = data.message || data.error || "Unknown error";
        jobStatus.value = "Error";
        addLog(`Error starting job: ${errorMessage}`);
        notify(`Failed to start job: ${errorMessage}`, "error");

        // Create a pseudo job entry for the error
        const pseudoJobName = `job-error-${Date.now()}`;
        currentJob.value = { job_name: pseudoJobName };
        jobStore.upsertJob({
          job_name: pseudoJobName,
          status: "Error",
          created_at: new Date().toISOString(),
          file_path: params.file_path,
          format: params.format,
          outcrs: params.outcrs,
          number: params.number,
          density:
            typeof params.density === "string"
              ? parseFloat(params.density)
              : params.density,
          roi: params.roi,
          remove_color: params.remove_color,
          remove_all_attributes: params.remove_all_attributes,
          line: params.line,
          returns: params.returns,
          last_updated: new Date().toISOString(),
          error_message: errorMessage,
        });
        jobStore.setCurrentJob(pseudoJobName);
        return;
      }

      // Success response - check for job_name
      const jobData = data as JobData;

      if (jobData.job_name) {
        currentJob.value = jobData;
        jobStatus.value = "Started";
        addLog(`Job started: ${jobData.job_name}`);
        notify(`Job ${jobData.job_name} started successfully`, "success");

        // Save job to store
        jobStore.upsertJob({
          job_name: jobData.job_name,
          status: "Started",
          created_at: new Date().toISOString(),
          file_path: params.file_path,
          format: params.format,
          outcrs: params.outcrs,
          number: params.number,
          density:
            typeof params.density === "string"
              ? parseFloat(params.density)
              : params.density,
          roi: params.roi,
          remove_color: params.remove_color,
          remove_all_attributes: params.remove_all_attributes,
          line: params.line,
          returns: params.returns,
          last_updated: new Date().toISOString(),
        });
        jobStore.setCurrentJob(jobData.job_name);

        listenForUpdates(jobData.job_name);
        return;
      }

      throw new Error("No job name received from server");
    } catch (error) {
      processing.value = false;
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      addLog(`Error starting job: ${errorMessage}`);
      notify(`Failed to start job: ${errorMessage}`, "error");
    }
  }

  // Setup WebSocket connection to listen for job updates
  function listenForUpdates(jobName: string): void {
    // Close any existing connection
    if (wsConnection && wsConnection.readyState !== WebSocket.CLOSED) {
      wsConnection.close();
    }

    const wsUrl = `${WS_BASE_URL}${PREFIX}/ws/job-status/${jobName}`;
    wsConnection = new WebSocket(wsUrl);

    wsConnection.onopen = (): void => {
      addLog("WebSocket connection established");
      notify("WebSocket connection established", "info");
    };

    wsConnection.onmessage = (event: MessageEvent): void => {
      try {
        const data = JSON.parse(event.data) as JobStatusResponse;
        addLog(data);
        notify(JSON.stringify(data), "info");

        // Update status and progress based on received data
        if (data.status) {
          jobStatus.value = data.status;

          // Update job in store
          jobStore.updateJobStatus(jobName, data.status, {
            error_message: data.logs || data.message,
          });
        }

        if (data.progress !== undefined) {
          // Check if progress is the new detailed object or legacy number
          if (typeof data.progress === "object" && data.progress !== null) {
            // New progress format with ETA
            progressInfo.value = data.progress;
            jobProgress.value = data.progress.percentage / 100; // Convert to 0-1 range
          } else {
            // Legacy format (simple number)
            jobProgress.value = data.progress;
            progressInfo.value = null;
          }
        }

        // On completion, show notification
        if (
          data.status === "Complete" ||
          data.status === "SuccessCriteriaMet"
        ) {
          notify("Processing complete. Download is ready!", "success");
        }

        // On error, show notification
        if (
          data.status === "Error" ||
          data.status === "Failed" ||
          data.status === "FailureTarget"
        ) {
          notify(
            "Job failed. Please check the status log for details.",
            "error",
          );
        }
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : String(error);
        addLog(`Error parsing WebSocket message: ${errorMessage}`);
      }
    };

    wsConnection.onerror = (event: Event): void => {
      addLog("WebSocket error occurred");
      console.error("WebSocket error:", event);
    };

    wsConnection.onclose = (event: CloseEvent): void => {
      addLog(`WebSocket connection closed (Code: ${event.code})`);
    };
  }

  // Check job status manually
  async function checkJobStatus(): Promise<void> {
    if (!currentJob.value?.job_name) return;

    checkingStatus.value = true;
    try {
      const response = await fetch(
        `${API_BASE_URL}${PREFIX}/job-status/${currentJob.value.job_name}`,
        {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
          },
        },
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = (await response.json()) as JobStatusResponse;
      checkingStatus.value = false;
      addLog(`Status check: ${JSON.stringify(data)}`);

      // Update status and progress
      if (data.status) {
        jobStatus.value = data.status;

        // Update job in store
        jobStore.updateJobStatus(currentJob.value!.job_name, data.status, {
          error_message: data.logs || data.message,
        });
      }

      if (data.progress !== undefined) {
        if (typeof data.progress === "object" && data.progress !== null) {
          progressInfo.value = data.progress;
          jobProgress.value = data.progress.percentage / 100;
        } else {
          jobProgress.value = data.progress;
          progressInfo.value = null;
        }
      } else if (
        data.status === "Complete" ||
        data.status === "SuccessCriteriaMet"
      ) {
        // If no progress info but job is complete, set to 100%
        jobProgress.value = 1;
      }

      notify(`Status updated: ${data.status}`, "info");
    } catch (error) {
      checkingStatus.value = false;
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      addLog(`Error checking job status: ${errorMessage}`);
      notify(`Failed to check status: ${errorMessage}`, "error");
    }
  }

  // Download the processed file
  async function downloadResult(): Promise<void> {
    if (!currentJob.value?.job_name) return;

    try {
      const url = `${API_BASE_URL}${PREFIX}/download/${currentJob.value.job_name}`;
      addLog(`Downloading from: ${url}`);
      notify("Starting download...", "info");

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);

      // Extract filename from Content-Disposition header or use a default
      let filename = "processed_pointcloud";
      const contentDisposition = response.headers.get("Content-Disposition");
      if (contentDisposition) {
        const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(
          contentDisposition,
        );
        if (matches && matches[1]) {
          filename = matches[1].replace(/['"]/g, "");
        }
      }

      // Create and trigger download link
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);

      addLog("Download complete");
      notify("Download complete!", "success");
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : String(error);
      addLog(`Download error: ${errorMessage}`);
      notify(`Download failed: ${errorMessage}`, "error");
    }
  }

  function resetJob(): void {
    // Reset all job-related state
    currentJob.value = null;
    jobStatus.value = "";
    jobProgress.value = 0;
    progressInfo.value = null;
    statusLogs.value = [];

    // Clear current job in store
    jobStore.setCurrentJob(null);

    // Close WebSocket if open
    closeConnection();
  }

  // Load a job from the store and reconnect to it
  async function loadJob(jobName: string): Promise<void> {
    const job = jobStore.getJob(jobName);
    if (!job) {
      notify("Job not found in history", "error");
      return;
    }

    // Mark that we're loading from history
    isLoadingFromHistory.value = true;

    // Set as current job
    currentJob.value = {
      ...job, // Include all job data
      job_name: job.job_name,
    };
    jobStatus.value = job.status;

    // Set progress to 100% if job is completed
    if (job.status === "Complete" || job.status === "SuccessCriteriaMet") {
      jobProgress.value = 1; // 100%
    } else {
      jobProgress.value = 0;
    }

    progressInfo.value = null;
    statusLogs.value = [];

    jobStore.setCurrentJob(job.job_name);

    addLog(`Loading job: ${job.job_name}`);

    // Check current status from server
    await checkJobStatus();

    // If still running, reconnect WebSocket
    if (jobStatus.value === "Running" || jobStatus.value === "Started") {
      listenForUpdates(job.job_name);
    }
  }

  // Get the loaded job parameters
  function getLoadedJobParams(): JobParams | null {
    if (!currentJob.value) return null;

    const job = currentJob.value as any;
    return {
      file_path: job.file_path || "",
      format: job.format,
      outcrs: job.outcrs,
      number: job.number,
      density: job.density,
      roi: job.roi,
      remove_color: job.remove_color,
      remove_all_attributes: job.remove_all_attributes,
      line: job.line,
      returns: job.returns,
    };
  }

  // Clean up WebSocket connection
  function closeConnection(): void {
    if (wsConnection && wsConnection.readyState !== WebSocket.CLOSED) {
      wsConnection.close();
    }
  }

  return {
    // State
    processing,
    currentJob,
    jobStatus,
    jobProgress,
    progressInfo,
    statusLogs,
    checkingStatus,
    isLoadingFromHistory,

    // Methods
    startJob,
    resetJob,
    loadJob,
    getLoadedJobParams,
    checkJobStatus,
    downloadResult,
    closeConnection,
    addLog,
  };
}
