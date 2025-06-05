// WebSocket and API services for file download operations
import { ref, Ref } from "vue";

// Define types for job-related data
interface JobLog {
  time: string;
  message: string;
}

interface JobData {
  job_name: string;
  [key: string]: any;
}

interface JobStatusResponse {
  status: string;
  progress?: number;
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
  [key: string]: any;
}

// Define notification handler type
type NotificationHandler = (message: string, type: string) => void;

export default function useDownloadService(
  // Optional custom notification handler
  notifyFn?: NotificationHandler
) {
  // Base URLs for API and WebSocket
  const API_BASE_URL = `${window.location.protocol}//${window.location.hostname}:${window.location.port}`;
  const WS_BASE_URL = `${
    window.location.protocol === "https:" ? "wss:" : "ws:"
  }//${window.location.hostname}:${window.location.port}`;
  const PREFIX = "/api";

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
  const statusLogs: Ref<JobLog[]> = ref([]);
  const checkingStatus: Ref<boolean> = ref(false);
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

    try {
      processing.value = true;
      addLog("Starting job...");

      const response = await fetch(`${API_BASE_URL}${PREFIX}/start-job/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = (await response.json()) as JobData;
      processing.value = false;

      if (data.job_name) {
        currentJob.value = data;
        jobStatus.value = "Started";
        addLog(`Job started: ${data.job_name}`);
        notify(`Job ${data.job_name} started successfully`, "success");
        listenForUpdates(data.job_name);
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
        }

        if (data.progress !== undefined) {
          jobProgress.value = data.progress;
        }

        // On completion, show notification
        if (
          data.status === "Complete" ||
          data.status === "SuccessCriteriaMet"
        ) {
          notify("Processing complete. Download is ready!", "success");
        }

        // On error, show notification
        if (data.status === "Error") {
          notify(
            "Job failed. Please check the status log for details.",
            "error"
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
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const data = (await response.json()) as JobStatusResponse;
      checkingStatus.value = false;
      addLog(`Status check: ${JSON.stringify(data)}`);

      // Update status and progress
      if (data.status) jobStatus.value = data.status;
      if (data.progress !== undefined) jobProgress.value = data.progress;

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
          contentDisposition
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
    statusLogs.value = [];

    // Close WebSocket if open
    closeConnection();
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
    statusLogs,
    checkingStatus,

    // Methods
    startJob,
    resetJob,
    checkJobStatus,
    downloadResult,
    closeConnection,
    addLog,
  };
}
