"""
Pod Log Collector Service

This service watches for pod failures and captures logs before they're deleted.
It runs as a background service and stores logs in the database or filesystem.
"""

from kubernetes import client, config, watch
import logging
import threading
from datetime import datetime
from typing import Optional, Dict
import os
from pathlib import Path

logger = logging.getLogger(__name__)

# Directory to store captured logs
LOG_STORAGE_PATH = os.getenv("POD_LOG_STORAGE_PATH", "/data/pod-logs")


class PodLogCollector:
    """Watches pods and captures logs when they fail or are terminated."""

    def __init__(self, namespace: str, label_selector: str = "addlidar.io/job-type"):
        """
        Initialize the pod log collector.

        Args:
            namespace: Kubernetes namespace to watch
            label_selector: Label selector to filter pods (e.g., "addlidar.io/job-type")
        """
        self.namespace = namespace
        self.label_selector = label_selector
        self.core_v1 = client.CoreV1Api()
        self.watching = False
        self.watch_thread = None

        # Ensure log storage directory exists
        Path(LOG_STORAGE_PATH).mkdir(parents=True, exist_ok=True)

    def capture_pod_logs(
        self,
        pod_name: str,
        container_name: Optional[str] = None,
        tail_lines: int = 5000,
    ) -> Optional[str]:
        """
        Capture logs from a pod.

        Args:
            pod_name: Name of the pod
            container_name: Specific container name (optional)
            tail_lines: Number of tail lines to capture

        Returns:
            Pod logs as string, or None if failed
        """
        try:
            kwargs = {
                "name": pod_name,
                "namespace": self.namespace,
                "tail_lines": tail_lines,
            }

            if container_name:
                kwargs["container"] = container_name

            logs = self.core_v1.read_namespaced_pod_log(**kwargs)
            return logs
        except Exception as e:
            logger.error(f"Failed to capture logs for pod {pod_name}: {e}")
            return None

    def save_logs_to_file(self, pod_name: str, logs: str, pod_status: dict) -> str:
        """
        Save logs to filesystem.

        Args:
            pod_name: Name of the pod
            logs: Log content
            pod_status: Pod status information

        Returns:
            Path to saved log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{pod_name}_{timestamp}.log"
        log_filepath = os.path.join(LOG_STORAGE_PATH, log_filename)

        try:
            with open(log_filepath, "w") as f:
                f.write(f"=== Pod Log Capture ===\n")
                f.write(f"Pod Name: {pod_name}\n")
                f.write(f"Namespace: {self.namespace}\n")
                f.write(f"Capture Time: {datetime.now().isoformat()}\n")
                f.write(f"Pod Phase: {pod_status.get('phase', 'Unknown')}\n")
                f.write(f"Reason: {pod_status.get('reason', 'N/A')}\n")
                f.write(f"Message: {pod_status.get('message', 'N/A')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(logs)

            logger.info(f"Saved logs for pod {pod_name} to {log_filepath}")
            return log_filepath
        except Exception as e:
            logger.error(f"Failed to save logs to file: {e}")
            return None

    def get_pod_status_info(self, pod) -> dict:
        """Extract relevant status information from pod object."""
        status_info = {
            "phase": pod.status.phase,
            "reason": None,
            "message": None,
        }

        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                if container_status.state.terminated:
                    status_info["reason"] = container_status.state.terminated.reason
                    status_info["message"] = container_status.state.terminated.message
                elif container_status.state.waiting:
                    status_info["reason"] = container_status.state.waiting.reason
                    status_info["message"] = container_status.state.waiting.message

        return status_info

    def should_capture_logs(self, pod) -> bool:
        """
        Determine if we should capture logs for this pod.

        Args:
            pod: Pod object from Kubernetes

        Returns:
            True if logs should be captured
        """
        # Capture logs for failed pods
        if pod.status.phase == "Failed":
            return True

        # Capture logs for pods with containers in error states
        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                if container_status.state.terminated:
                    reason = container_status.state.terminated.reason
                    # Capture for OOMKilled, Error, etc.
                    if reason in ["OOMKilled", "Error", "DeadlineExceeded"]:
                        return True
                    # Capture for non-zero exit codes
                    if container_status.state.terminated.exit_code != 0:
                        return True

        return False

    def watch_pods(self):
        """
        Watch pods and capture logs when they fail.
        This runs in a separate thread.
        """
        logger.info(
            f"Starting pod watcher for namespace {self.namespace} with label selector {self.label_selector}"
        )

        w = watch.Watch()
        self.watching = True

        try:
            for event in w.stream(
                self.core_v1.list_namespaced_pod,
                namespace=self.namespace,
                label_selector=self.label_selector,
            ):
                if not self.watching:
                    logger.info("Stopping pod watcher")
                    w.stop()
                    break

                event_type = event["type"]
                pod = event["object"]
                pod_name = pod.metadata.name

                # Only process MODIFIED and DELETED events
                if event_type in ["MODIFIED", "DELETED"]:
                    if self.should_capture_logs(pod):
                        logger.warning(
                            f"Capturing logs for {event_type} pod {pod_name} in phase {pod.status.phase}"
                        )

                        # Get all containers in the pod
                        containers = [c.name for c in pod.spec.containers]

                        for container_name in containers:
                            logs = self.capture_pod_logs(pod_name, container_name)
                            if logs:
                                pod_status = self.get_pod_status_info(pod)
                                log_file = self.save_logs_to_file(
                                    f"{pod_name}_{container_name}", logs, pod_status
                                )
                                if log_file:
                                    logger.info(
                                        f"Successfully captured logs for {pod_name}/{container_name}"
                                    )

        except Exception as e:
            logger.error(f"Error in pod watcher: {e}")
        finally:
            self.watching = False
            logger.info("Pod watcher stopped")

    def start(self):
        """Start the pod watcher in a background thread."""
        if self.watch_thread and self.watch_thread.is_alive():
            logger.warning("Pod watcher already running")
            return

        self.watch_thread = threading.Thread(target=self.watch_pods, daemon=True)
        self.watch_thread.start()
        logger.info("Pod watcher thread started")

    def stop(self):
        """Stop the pod watcher."""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=5)
        logger.info("Pod watcher stopped")


# Global instance
_collector_instance: Optional[PodLogCollector] = None


def get_pod_log_collector(namespace: str) -> PodLogCollector:
    """Get or create the global pod log collector instance."""
    global _collector_instance

    if _collector_instance is None:
        _collector_instance = PodLogCollector(namespace=namespace)

    return _collector_instance


def start_pod_log_collector(namespace: str):
    """Start the global pod log collector."""
    collector = get_pod_log_collector(namespace)
    collector.start()
    logger.info(f"Pod log collector started for namespace {namespace}")
