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
import time

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

        # Load Kubernetes configuration
        try:
            config.load_incluster_config()
            logger.info("Loaded Kubernetes in-cluster config for pod log collector")
        except config.ConfigException:
            logger.warning("Failed to load in-cluster config, trying local kubeconfig")
            try:
                config.load_kube_config()
                logger.info("Loaded local Kubernetes config for pod log collector")
            except Exception as e:
                logger.error(f"Failed to load any Kubernetes config: {e}")
                raise

        self.core_v1 = client.CoreV1Api()
        self.watching = False
        self.watch_thread = None
        self._captured_pods = set()  # Track pods we've already captured logs for

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
        except client.exceptions.ApiException as e:
            # If pod is not found (404), it was likely already deleted - this is expected
            if e.status == 404:
                logger.debug(
                    f"Pod {pod_name} not found when capturing logs (likely already deleted)"
                )
            else:
                logger.error(f"Failed to capture logs for pod {pod_name}: {e}")
            return None
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
                f.write(f"Exit Code: {pod_status.get('exit_code', 'N/A')}\n")
                f.write(f"Signal: {pod_status.get('signal', 'N/A')}\n")
                f.write(f"Started At: {pod_status.get('started_at', 'N/A')}\n")
                f.write(f"Finished At: {pod_status.get('finished_at', 'N/A')}\n")
                f.write("=" * 80 + "\n\n")
                f.write(logs)

            logger.info(f"Saved logs for pod {pod_name} to {log_filepath}")
            return log_filepath
        except Exception as e:
            logger.error(f"Failed to save logs to file: {e}")
            return None

    def save_deletion_metadata(
        self, pod_name: str, pod, pod_status: dict
    ) -> Optional[str]:
        """
        Save pod metadata when logs cannot be captured (e.g., pod already deleted).

        Args:
            pod_name: Name of the pod
            pod: Pod object from Kubernetes
            pod_status: Pod status information

        Returns:
            Path to saved metadata file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata_filename = f"{pod_name}_{timestamp}_metadata.txt"
        metadata_filepath = os.path.join(LOG_STORAGE_PATH, metadata_filename)

        try:
            with open(metadata_filepath, "w") as f:
                f.write(f"=== Pod Failure Metadata ===\n")
                f.write(f"Pod Name: {pod_name}\n")
                f.write(f"Namespace: {self.namespace}\n")
                f.write(f"Capture Time: {datetime.now().isoformat()}\n")
                f.write(f"Pod Phase: {pod_status.get('phase', 'Unknown')}\n")
                f.write(
                    f"Deletion Timestamp: {pod.metadata.deletion_timestamp or 'N/A'}\n"
                )
                f.write(
                    f"Creation Timestamp: {pod.metadata.creation_timestamp or 'N/A'}\n"
                )
                f.write("=" * 80 + "\n\n")

                # Container statuses
                f.write("=== Container Statuses ===\n")
                if pod.status.container_statuses:
                    for cs in pod.status.container_statuses:
                        f.write(f"\nContainer: {cs.name}\n")
                        f.write(f"  Ready: {cs.ready}\n")
                        f.write(f"  Restart Count: {cs.restart_count}\n")

                        if cs.state.terminated:
                            term = cs.state.terminated
                            f.write(f"  State: Terminated\n")
                            f.write(f"    Reason: {term.reason}\n")
                            f.write(f"    Message: {term.message}\n")
                            f.write(f"    Exit Code: {term.exit_code}\n")
                            f.write(f"    Signal: {term.signal}\n")
                            f.write(f"    Started At: {term.started_at}\n")
                            f.write(f"    Finished At: {term.finished_at}\n")
                        elif cs.state.waiting:
                            f.write(f"  State: Waiting\n")
                            f.write(f"    Reason: {cs.state.waiting.reason}\n")
                            f.write(f"    Message: {cs.state.waiting.message}\n")
                        elif cs.state.running:
                            f.write(f"  State: Running\n")
                            f.write(f"    Started At: {cs.state.running.started_at}\n")
                else:
                    f.write("  No container statuses available\n")

                # Pod conditions
                f.write("\n=== Pod Conditions ===\n")
                if pod.status.conditions:
                    for condition in pod.status.conditions:
                        f.write(f"\n{condition.type}:\n")
                        f.write(f"  Status: {condition.status}\n")
                        f.write(f"  Reason: {condition.reason}\n")
                        f.write(f"  Message: {condition.message}\n")
                        f.write(
                            f"  Last Transition: {condition.last_transition_time}\n"
                        )
                else:
                    f.write("  No conditions available\n")

                # Events (if we can fetch them)
                f.write("\n=== Recent Pod Events ===\n")
                try:
                    events = self.core_v1.list_namespaced_event(
                        namespace=self.namespace,
                        field_selector=f"involvedObject.name={pod_name}",
                    )
                    if events.items:
                        for event in sorted(
                            events.items,
                            key=lambda e: e.last_timestamp
                            or e.event_time
                            or datetime.min,
                            reverse=True,
                        )[
                            :10
                        ]:  # Last 10 events
                            f.write(
                                f"\n[{event.last_timestamp or event.event_time}] "
                                f"{event.type}: {event.reason}\n"
                            )
                            f.write(f"  {event.message}\n")
                    else:
                        f.write("  No events found\n")
                except Exception as e:
                    f.write(f"  Could not fetch events: {e}\n")

                # Labels and annotations
                f.write("\n=== Labels ===\n")
                if pod.metadata.labels:
                    for key, value in pod.metadata.labels.items():
                        f.write(f"  {key}: {value}\n")
                else:
                    f.write("  No labels\n")

                f.write("\n=== Annotations ===\n")
                if pod.metadata.annotations:
                    for key, value in pod.metadata.annotations.items():
                        f.write(f"  {key}: {value}\n")
                else:
                    f.write("  No annotations\n")

                # Owner references (to find parent Job)
                f.write("\n=== Owner References ===\n")
                if pod.metadata.owner_references:
                    for owner in pod.metadata.owner_references:
                        f.write(f"  Kind: {owner.kind}\n")
                        f.write(f"  Name: {owner.name}\n")
                        f.write(f"  UID: {owner.uid}\n")
                        f.write(f"  Controller: {owner.controller}\n")
                else:
                    f.write("  No owner references\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write(
                    "NOTE: Pod logs could not be captured (pod likely already deleted)\n"
                )

            logger.info(f"Saved metadata for pod {pod_name} to {metadata_filepath}")
            return metadata_filepath
        except Exception as e:
            logger.error(f"Failed to save metadata to file: {e}")
            return None

    def get_pod_status_info(self, pod) -> dict:
        """Extract relevant status information from pod object."""
        status_info = {
            "phase": pod.status.phase,
            "reason": None,
            "message": None,
            "exit_code": None,
            "signal": None,
            "started_at": None,
            "finished_at": None,
        }

        if pod.status.container_statuses:
            for container_status in pod.status.container_statuses:
                if container_status.state.terminated:
                    term = container_status.state.terminated
                    status_info["reason"] = term.reason
                    status_info["message"] = term.message
                    status_info["exit_code"] = term.exit_code
                    status_info["signal"] = term.signal
                    status_info["started_at"] = (
                        term.started_at.isoformat() if term.started_at else None
                    )
                    status_info["finished_at"] = (
                        term.finished_at.isoformat() if term.finished_at else None
                    )
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

                # Process all event types to maximize information capture
                if event_type in ["ADDED", "MODIFIED", "DELETED"]:
                    if self.should_capture_logs(pod):
                        # Check if we've already captured logs for this pod
                        if pod_name in self._captured_pods:
                            # For DELETED events, still save metadata even if we captured logs before
                            if event_type == "DELETED":
                                logger.info(
                                    f"Pod {pod_name} deleted - saving deletion metadata"
                                )
                                pod_status = self.get_pod_status_info(pod)
                                self.save_deletion_metadata(pod_name, pod, pod_status)
                            else:
                                logger.debug(
                                    f"Already captured logs for {pod_name}, skipping"
                                )
                            continue

                        logger.warning(
                            f"Capturing logs for {event_type} pod {pod_name} in phase {pod.status.phase}"
                        )

                        # Mark pod as captured before attempting to prevent race conditions
                        self._captured_pods.add(pod_name)

                        # Get all containers in the pod
                        containers = [c.name for c in pod.spec.containers]

                        captured_any = False
                        for container_name in containers:
                            # For DELETED events, try once (pod likely already gone)
                            # For other events, retry multiple times
                            max_retries = 1 if event_type == "DELETED" else 3

                            for attempt in range(max_retries):
                                logs = self.capture_pod_logs(pod_name, container_name)
                                if logs:
                                    pod_status = self.get_pod_status_info(pod)
                                    log_file = self.save_logs_to_file(
                                        f"{pod_name}_{container_name}", logs, pod_status
                                    )
                                    if log_file:
                                        logger.info(
                                            f"Successfully captured logs for {pod_name}/{container_name} (event: {event_type})"
                                        )
                                        captured_any = True
                                        break
                                elif attempt < max_retries - 1:
                                    # Brief delay before retry
                                    time.sleep(0.5)

                        # For DELETED events or if log capture failed, save whatever metadata we have
                        if not captured_any or event_type == "DELETED":
                            pod_status = self.get_pod_status_info(pod)
                            self.save_deletion_metadata(pod_name, pod, pod_status)
                            if not captured_any:
                                logger.warning(
                                    f"Could not capture logs for {pod_name}, but saved metadata"
                                )

                        # If we failed to capture any logs on non-DELETED events, remove from tracking
                        # to allow retry on next event
                        if not captured_any and event_type != "DELETED":
                            self._captured_pods.discard(pod_name)

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

        # Clean up dead thread reference if it exists
        if self.watch_thread and not self.watch_thread.is_alive():
            logger.info("Cleaning up dead pod watcher thread")
            self.watch_thread = None

        self.watch_thread = threading.Thread(target=self.watch_pods, daemon=True)
        self.watch_thread.start()
        logger.info("Pod watcher thread started")

        # Give the thread a moment to start and log its "Starting pod watcher" message
        import time

        time.sleep(0.1)

    def stop(self):
        """Stop the pod watcher."""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=5)
        logger.info("Pod watcher stopped")


# Global instance
_collector_instance: Optional[PodLogCollector] = None
_collector_started: bool = False


def get_pod_log_collector(namespace: str) -> PodLogCollector:
    """Get or create the global pod log collector instance."""
    global _collector_instance

    if _collector_instance is None:
        _collector_instance = PodLogCollector(namespace=namespace)

    return _collector_instance


def start_pod_log_collector(namespace: str):
    """Start the global pod log collector (only once across all workers)."""
    global _collector_started

    if _collector_started:
        logger.debug("Pod log collector already started in this process")
        return

    _collector_started = True
    collector = get_pod_log_collector(namespace)
    collector.start()
    logger.info(f"Pod log collector started for namespace {namespace}")
