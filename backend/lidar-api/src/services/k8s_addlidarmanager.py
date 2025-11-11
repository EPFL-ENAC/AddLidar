from kubernetes import client, config
from kubernetes.watch import Watch
from kubernetes.stream import stream
import uuid
import logging
import asyncio
import os
import re
import time
import threading
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.config.settings import settings
from src.utils.kubernetes_utils import get_node_scheduling_config

# from src.services.job_status import job_status_manager


logger = logging.getLogger(__name__)

# Load Kubernetes config
try:
    config.load_kube_config()
    logger.info("Using kubeconfig for authentication")
except Exception as e:
    logger.info(f"Could not load kubeconfig: {str(e)}")
    config.load_incluster_config()
    logger.info("Using in-cluster configuration")
batch_v1 = client.BatchV1Api()

# Store WebSocket connections
active_connections: Dict[str, Any] = {}

# Dictionary to control running watch loops
watch_control: Dict[str, bool] = {}

AUTHORIZED_STATUSES = ["Complete", "SuccessCriteriaMet", "Failed", "FailureTarget"]


class JobStatus(BaseModel):
    """Model representing the status of a job."""

    job_name: Optional[str]
    status: Optional[str]
    message: Optional[str]
    created_at: Optional[datetime] = None
    total_time: Optional[float] = None  # in seconds
    timestamp: Optional[datetime] = None
    cli_args: Optional[List[str]] = None
    output_path: Optional[str] = None
    logs: Optional[str] = None  # Changed from bytes to str
    progress: Optional[Dict[str, Any]] = None  # Progress information with ETA

    class Config:
        json_encoders = {
            # Custom JSON encoder for datetime
            datetime: lambda dt: dt.isoformat() if dt else None
        }


# Store job statuses in memory
job_statuses: Dict[str, Dict[str, Any]] = {}

# Track log streaming threads
log_stream_control: Dict[str, bool] = {}


def parse_progress_from_log(log_line: str) -> Optional[Dict[str, Any]]:
    """
    Parse progress information from log lines like:
    'Processed 157692/1484192264'

    Returns:
        Dict with processed, total, percentage, or None if not a progress line
    """
    match = re.match(r"Processed\s+(\d+)/(\d+)", log_line)
    if match:
        processed = int(match.group(1))
        total = int(match.group(2))
        percentage = (processed / total * 100) if total > 0 else 0
        return {
            "processed": processed,
            "total": total,
            "percentage": round(percentage, 2),
        }
    return None


def calculate_eta(
    processed: int, total: int, start_time: float, current_time: float
) -> Optional[Dict[str, Any]]:
    """
    Calculate estimated time of arrival based on processing speed.

    Args:
        processed: Number of items processed
        total: Total number of items
        start_time: Job start time (epoch)
        current_time: Current time (epoch)

    Returns:
        Dict with eta_seconds, points_per_second, estimated_completion_time
    """
    if processed <= 0 or total <= 0:
        return None

    elapsed_time = current_time - start_time
    if elapsed_time <= 0:
        return None

    points_per_second = processed / elapsed_time
    remaining_points = total - processed
    eta_seconds = remaining_points / points_per_second if points_per_second > 0 else 0
    estimated_completion = current_time + eta_seconds

    return {
        "eta_seconds": round(eta_seconds, 2),
        "points_per_second": round(points_per_second, 2),
        "estimated_completion_time": datetime.fromtimestamp(
            estimated_completion
        ).isoformat(),
        "elapsed_seconds": round(elapsed_time, 2),
    }


def stream_pod_logs(
    job_name: str, pod_name: str, namespace: str, loop: asyncio.AbstractEventLoop
) -> None:
    """
    Stream logs from a running pod and parse progress information.
    Uses polling with timeout to avoid blocking when Kubernetes buffers logs.

    Args:
        job_name: Name of the job
        pod_name: Name of the pod to stream logs from
        namespace: Kubernetes namespace
        loop: Event loop for async operations
    """
    try:
        core_v1 = client.CoreV1Api()
        log_stream_control[job_name] = True

        logger.info(f"Starting log stream for job {job_name}, pod {pod_name}")

        # Get job start time from job_statuses or use current time
        job_status_info = job_statuses.get(job_name, {})
        start_time = job_status_info.get("created_at")
        if isinstance(start_time, datetime):
            start_time = start_time.timestamp()
        elif start_time is None:
            start_time = time.time()

        # Track the last line we've seen to avoid re-parsing
        last_log_position = 0
        last_progress_info = None
        poll_interval = 2  # Poll logs every 2 seconds
        heartbeat_interval = 5  # Send heartbeat every 5 seconds even without new logs

        last_heartbeat_time = time.time()

        # Wait for pod to be in Running state before polling logs
        pod_ready = False
        while log_stream_control.get(job_name, False) and not pod_ready:
            try:
                pod = core_v1.read_namespaced_pod(name=pod_name, namespace=namespace)
                if pod.status.phase == "Running":
                    pod_ready = True
                    logger.info(f"Pod {pod_name} is now Running, starting log polling")
                else:
                    logger.debug(
                        f"Waiting for pod {pod_name} to be Running (current: {pod.status.phase})"
                    )
                    time.sleep(2)
            except Exception as e:
                logger.error(f"Error checking pod status: {str(e)}")
                time.sleep(2)

        if not log_stream_control.get(job_name, False):
            logger.info(f"Log streaming stopped before pod was ready for {job_name}")
            return

        while log_stream_control.get(job_name, False):
            try:
                # Fetch logs with tail_lines to get recent logs without streaming
                # This is non-blocking and returns immediately
                logs = core_v1.read_namespaced_pod_log(
                    name=pod_name,
                    namespace=namespace,
                    timestamps=False,
                )

                if logs:
                    # Split logs into lines
                    all_lines = re.split(r"[\r\n]+", logs)

                    logger.debug(
                        f"Polled logs for {job_name}: {len(all_lines)} total lines, last position: {last_log_position}"
                    )

                    # Process only new lines since last position
                    if len(all_lines) > last_log_position:
                        new_lines = all_lines[last_log_position:]
                        last_log_position = len(all_lines)

                        logger.debug(f"Found {len(new_lines)} new lines for {job_name}")

                        # Parse progress from new lines
                        for line in new_lines:
                            line = line.strip()
                            if not line:
                                continue

                            progress_info = parse_progress_from_log(line)
                            if progress_info:
                                last_progress_info = progress_info
                                logger.debug(
                                    f"Parsed progress for {job_name}: {progress_info['processed']}/{progress_info['total']}"
                                )

                # Send update if we have progress info
                current_time = time.time()
                if last_progress_info:
                    # Calculate ETA
                    eta_info = calculate_eta(
                        last_progress_info["processed"],
                        last_progress_info["total"],
                        start_time,
                        current_time,
                    )

                    if eta_info:
                        last_progress_info.update(eta_info)

                    # Send progress update
                    logger.debug(
                        f"Sending progress update for {job_name}: {last_progress_info['percentage']:.1f}%"
                    )
                    update_job_statuses(
                        job_name,
                        JobStatus(
                            job_name=job_name,
                            status="Running",
                            message=f"Processing: {last_progress_info['processed']}/{last_progress_info['total']} ({last_progress_info['percentage']:.1f}%)",
                            progress=last_progress_info,
                        ),
                        loop,
                    )
                    last_heartbeat_time = current_time
                elif current_time - last_heartbeat_time >= heartbeat_interval:
                    # Send heartbeat even without progress to keep connection alive
                    logger.debug(f"Sending heartbeat for {job_name}")
                    update_job_statuses(
                        job_name,
                        JobStatus(
                            job_name=job_name,
                            status="Running",
                            message="Job is running (waiting for log updates)",
                        ),
                        loop,
                    )
                    last_heartbeat_time = current_time

                # Sleep before next poll
                time.sleep(poll_interval)

            except client.exceptions.ApiException as api_error:
                if api_error.status == 404:
                    logger.info(f"Pod {pod_name} not found, stopping log stream")
                    break
                else:
                    logger.error(f"API error fetching logs: {str(api_error)}")
                    time.sleep(poll_interval)
            except Exception as poll_error:
                logger.error(f"Error polling logs: {str(poll_error)}")
                time.sleep(poll_interval)

        logger.info(f"Log stream ended for job {job_name}")

    except Exception as e:
        logger.error(f"Error setting up log stream for job {job_name}: {str(e)}")
    finally:
        # Clean up
        if job_name in log_stream_control:
            del log_stream_control[job_name]


def start_log_streaming(job_name: str, namespace: str) -> None:
    """
    Start streaming logs for a job in a separate thread.
    Will retry if pod is not ready yet.

    Args:
        job_name: Name of the job
        namespace: Kubernetes namespace
    """
    try:
        logger.info(f"start_log_streaming called for job {job_name}")
        # Get the pod name for this job
        core_v1 = client.CoreV1Api()
        pods = core_v1.list_namespaced_pod(
            namespace=namespace, label_selector=f"job-name={job_name}"
        )

        if not pods.items:
            logger.warning(
                f"No pods found for job {job_name}, will retry when pod is ready"
            )
            return

        pod_name = pods.items[0].metadata.name
        pod_phase = pods.items[0].status.phase

        logger.info(f"Pod {pod_name} for job {job_name} is in phase: {pod_phase}")

        # Start log streaming thread regardless of pod phase
        # The thread will wait for the pod to be Running
        loop = asyncio.get_event_loop()
        thread = threading.Thread(
            target=stream_pod_logs,
            args=(job_name, pod_name, namespace, loop),
            daemon=True,
        )
        thread.start()
        logger.info(
            f"Started log streaming thread for job {job_name} (pod phase: {pod_phase})"
        )

    except Exception as e:
        logger.error(f"Error starting log stream for job {job_name}: {str(e)}")


def stop_log_streaming(job_name: str) -> None:
    """
    Stop streaming logs for a job.

    Args:
        job_name: Name of the job
    """
    if job_name in log_stream_control:
        log_stream_control[job_name] = False
        logger.info(f"Stopped log streaming for job {job_name}")


def update_job_statuses(
    job_name: str, job_status: JobStatus, loop: asyncio.AbstractEventLoop
) -> None:
    """
    Update the status of a job in the job_statuses dictionary.
    Only updates fields that are provided in the new status, preserving existing values.

    Args:
        job_name: Name of the job to update
        job_status: Status information for the job
        loop: Event loop to schedule async tasks on
    """
    # Get current job status if it exists
    current_status = job_statuses.get(job_name, {})

    # Convert new status to dict
    new_status = job_status.dict(exclude_unset=True, exclude_none=True)

    # Merge statuses, preserving existing values for fields not in new_status
    merged_status = {**current_status, **new_status}
    merged_status["timestamp"] = datetime.now()

    # Store the merged status
    job_statuses[job_name] = merged_status

    # Use the passed event loop to notify connected WebSocket clients
    if job_name in active_connections:
        # Use JobStatus object directly instead of dict to avoid type issues
        status_object = JobStatus(**merged_status)
        asyncio.run_coroutine_threadsafe(notify_websocket(status_object), loop)

    logger.debug(f"Updated job status for {job_name}: {merged_status}")


def get_settings() -> Dict[str, Any]:
    """
    Get settings from environment variables or use defaults.

    Returns:
        Dict[str, Any]: Dictionary of configuration settings with effective namespace
    """
    settings_dict = settings.dict()
    # Use the effective namespace (with runtime detection)
    settings_dict["NAMESPACE"] = settings.effective_namespace
    return settings_dict


def get_pod_info(pod_name: str) -> str:
    """
    Get information about a pod.

    Args:
        pod_name: Name of the pod to get information for

    Returns:
        str: Information about the pod
    """
    core_v1 = client.CoreV1Api()
    settings_dict = get_settings()
    pod = core_v1.read_namespaced_pod(
        name=pod_name, namespace=settings_dict["NAMESPACE"]
    )
    pod_info = f"Pod phase: {pod.status.phase}\n"
    if pod.status.container_statuses:
        for container in pod.status.container_statuses:
            pod_info += f"Container {container.name} ready: {container.ready}\n"
            if container.state.waiting:
                pod_info += f"  Waiting: {container.state.waiting.reason} - {container.state.waiting.message}\n"
            if container.state.terminated:
                pod_info += (
                    f"  Terminated: {container.state.terminated.reason} - "
                    f"Exit code: {container.state.terminated.exit_code} - "
                    f"Message: {container.state.terminated.message}\n"
                )
    return pod_info


def get_log_job_status(job_name: str) -> str:
    # Get the pod associated with the job
    settings_dict = get_settings()

    label_selector = f"job-name={job_name}"
    core_v1 = client.CoreV1Api()
    pods = core_v1.list_namespaced_pod(
        namespace=settings_dict["NAMESPACE"], label_selector=label_selector
    )

    if not pods.items:
        logger.error(f"No pods found for job {job_name}")
        return b"No pods found for this job", 1, None

    pod_name = pods.items[0].metadata.name
    logger.info(f"Pod name: {pod_name}")

    try:
        # Get the logs
        logs = core_v1.read_namespaced_pod_log(
            name=pod_name, namespace=settings_dict["NAMESPACE"]
        )

        # if not logs or logs == "\n":
        #     # If logs are empty, try to get pod status information
        #     logs = get_pod_info(pod_name)
        # else:
        #     return logs
        if not logs or logs == "\n":
            logs = "No logs available\n"
        return logs + "\n" + get_pod_info(pod_name)

    except Exception as e:
        logger.error(f"Error getting logs for job {job_name}: {str(e)}")
        return f"Error retrieving logs: {str(e)}"


def watch_job_status_thread(
    job_name: str, namespace: str, loop: asyncio.AbstractEventLoop
) -> None:
    """
    Watches a Kubernetes Job in a separate thread and sends status updates via event loop.

    Args:
        job_name: Name of the job to watch
        namespace: Kubernetes namespace where the job exists
        loop: Event loop to schedule async tasks on
    """
    try:
        batch_v1 = client.BatchV1Api()
        w = Watch()
        watch_control[job_name] = True
        log_streaming_started = False

        logger.info(f"Started watching job {job_name} in namespace {namespace}")

        for event in w.stream(batch_v1.list_namespaced_job, namespace=namespace):
            # Check if we should stop watching
            if not watch_control.get(job_name, True):
                logger.info(f"Stopping watch for job {job_name}")
                stop_log_streaming(job_name)
                w.stop()
                break

            job = event["object"]

            if job.metadata.name == job_name:
                conditions = job.status.conditions

                # Then use methods
                # status = job_status_manager.get_detailed_job_status(job_name)
                # simple_status = job_status_manager.interpret_job_status(status)
                # logger.info(f"Simple status: {simple_status}")
                if job.status.active == 1:
                    logger.info(
                        f"Job {job_name} is active/running, status: {str(job.status)}"
                    )
                    update_job_statuses(
                        job_name,
                        JobStatus(
                            job_name=job_name,
                            status="Running",
                            message="Job is running",
                        ),
                        loop,
                    )

                    # Start log streaming when job starts running (only once)
                    if not log_streaming_started:
                        logger.info(
                            f"Attempting to start log streaming for job {job_name}"
                        )
                        start_log_streaming(job_name, namespace)
                        log_streaming_started = True
                        logger.info(f"Log streaming start requested for job {job_name}")

                if conditions:
                    status = conditions[0].type
                    logs = None
                    if status in AUTHORIZED_STATUSES:
                        # Stop log streaming before getting final logs
                        stop_log_streaming(job_name)

                        try:
                            logs = get_log_job_status(job_name)
                        except Exception as log_error:
                            logger.error(
                                f"Error getting logs for job {job_name}: {str(log_error)}"
                            )
                            logs = f"Error retrieving logs: {str(log_error)}"

                    update_job_statuses(
                        job_name,
                        JobStatus(
                            job_name=job_name,
                            status=status,
                            message=f"Job {job_name} {status}",
                            logs=logs if logs else "no logs",
                        ),
                        loop,
                    )
                    if status in AUTHORIZED_STATUSES:
                        delete_k8s_job(job_name, namespace)
                        w.stop()
                        break

    except Exception as e:
        logger.error(f"Error watching job {job_name}: {str(e)}")
        stop_log_streaming(job_name)
        update_job_statuses(
            job_name,
            JobStatus(
                job_name=job_name,
                status="Error",
                message=f"Error watching job: {str(e)}",
            ),
            loop,
        )
    finally:
        # Clean up the watch control entry and log streaming
        stop_log_streaming(job_name)
        if job_name in watch_control:
            logger.info(f"Cleaning up watch control: {job_name}")
            del watch_control[job_name]


async def notify_websocket(job_status: JobStatus) -> None:
    """
    Send a message to WebSocket client.

    Args:
        job_status: Status information for the job including job_name
                    Can be either a JobStatus object or a dictionary
    """
    try:
        job_name = extract_job_name(job_status)
        if not job_name:
            logger.error(f"Job name is missing in job status: {job_status}")
            return

        if job_name in active_connections:
            connection = active_connections[job_name]
            status_dict = prepare_status_dict(job_status)
            await connection.send_json(status_dict)
            logger.info(
                f"WebSocket notification sent for job {job_name}: {job_status.message}"
            )

            if job_status.status in AUTHORIZED_STATUSES:
                await connection.close()
                logger.info(f"Closed WebSocket for completed job {job_name}")
                del active_connections[job_name]
    except Exception as e:
        handle_notification_error(e, job_status)


def extract_job_name(job_status: JobStatus) -> Optional[str]:
    if not isinstance(job_status, JobStatus):
        raise ValueError("job_status must be a JobStatus object")
    return job_status.job_name


def prepare_status_dict(job_status: JobStatus) -> Dict[str, Any]:
    status_dict = job_status.dict(exclude_unset=True)
    if status_dict.get("timestamp") and isinstance(status_dict["timestamp"], datetime):
        status_dict["timestamp"] = status_dict["timestamp"].isoformat()
    if status_dict.get("created_at") and isinstance(
        status_dict["created_at"], datetime
    ):
        status_dict["created_at"] = status_dict["created_at"].isoformat()
    if "logs" in status_dict and isinstance(status_dict["logs"], bytes):
        status_dict["logs"] = status_dict["logs"].decode("utf-8", errors="replace")
    if status_dict.get("timestamp") and status_dict.get("created_at"):
        timestamp = datetime.fromisoformat(status_dict["timestamp"])
        created_at = datetime.fromisoformat(status_dict["created_at"])
        status_dict["total_time"] = (timestamp - created_at).total_seconds()
    return status_dict


def handle_notification_error(e: Exception, job_status: JobStatus) -> None:
    job_name_str = "unknown"
    try:
        job_name_str = (
            job_status.job_name
            if isinstance(job_status, JobStatus)
            else job_status.get("job_name", "unknown")
        )
        logger.error(f"Error notifying WebSocket for job {job_name_str}: {str(e)}")
        if job_name_str in active_connections:
            del active_connections[job_name_str]
    except Exception as nested_e:
        logger.error(
            f"Critical error in notify_websocket error handler: {str(nested_e)}"
        )


def stop_watching_job(job_name: str) -> None:
    """
    Stops watching a job and stops log streaming.

    Args:
        job_name: Name of the job to stop watching
    """
    if job_name in watch_control:
        watch_control[job_name] = False
        logger.info(f"Stopping job watcher for job {job_name}")
    else:
        logger.warning(f"No watch control found for job {job_name}")

    # Also stop log streaming
    stop_log_streaming(job_name)


def start_watching_job(job_name: str, namespace: str = "default") -> None:
    """
    Starts watching a job in a separate thread.

    Args:
        job_name: Name of the job to watch
        namespace: Kubernetes namespace where the job exists
    """
    # Clean up any existing watch for this job
    if job_name in watch_control:
        watch_control[job_name] = False

    # Capture the current event loop to pass to the thread
    loop = asyncio.get_event_loop()
    try:
        # Start new watch thread
        thread = threading.Thread(
            target=watch_job_status_thread,
            args=(job_name, namespace, loop),
            daemon=True,
        )
        thread.start()
        logger.info(f"Started job watcher thread for job {job_name}")
    except RuntimeError as e:
        update_job_statuses(
            job_name,
            JobStatus(
                job_name=job_name,
                status="Error",
                message=f"Failed to start job watcher: {str(e)}",
            ),
            loop,
        )


def register_websocket(job_name: str, websocket) -> None:
    """
    Register a WebSocket connection for a job.

    Args:
        job_name: The job name to associate the WebSocket with
        websocket: The WebSocket connection object
    """
    active_connections[job_name] = websocket
    logger.info(f"Registered WebSocket for job {job_name}")

    # If we already have status for this job, send it immediately
    if job_name in job_statuses:
        status_dict = job_statuses[job_name]
        # Convert to JobStatus object to ensure type safety
        status_object = JobStatus(**status_dict)
        asyncio.create_task(notify_websocket(status_object))


def delete_k8s_job(job_name: str, namespace: str) -> bool:
    """
    Delete a Kubernetes job.

    Args:
        job_name: Name of the job to delete
        namespace: Kubernetes namespace where the job exists

    Returns:
        bool: True if deletion was successful, False otherwise
    """
    try:
        batch_v1 = client.BatchV1Api()
        delete_options = client.V1DeleteOptions(propagation_policy="Background")
        batch_v1.delete_namespaced_job(
            name=job_name, namespace=namespace, body=delete_options
        )
        logger.info(f"Deleted job {job_name}")
        return True
    except Exception as e:
        logger.warning(f"Failed to delete job {job_name}: {str(e)}")
        return False


def generate_k8s_addlidarmanager_job(
    job_name: str, unique_filename: str, cli_args: Optional[List[str]]
) -> None:
    """
    Create a Kubernetes job that runs the LidarDataManager container.

    Args:
        job_name: Name of the job to create
        cli_args: CLI arguments to pass to the container

    Returns:
        str: The name of the created job
    """
    settings_dict = get_settings()
    container_output_path = f"{settings_dict['OUTPUT_PATH']}/{unique_filename}"

    # Add the output file argument to CLI args
    output_args = [f"-o={container_output_path}"]
    full_cli_args = cli_args + output_args

    # The container image to use
    container_image = f"{settings_dict['IMAGE_NAME']}:{settings_dict['IMAGE_TAG']}"

    logger.info(f"Creating job {job_name} with command: {full_cli_args}")
    logger.info(f"Using container image: {container_image}")

    # Create API clients
    batch_v1 = client.BatchV1Api()

    # Define volume and volume mounts for PVC
    volumes = [
        client.V1Volume(
            name="data-volume",
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                claim_name=settings_dict["PVC_NAME"]
            ),
        ),
        client.V1Volume(
            name="data-output-volume",
            persistent_volume_claim=client.V1PersistentVolumeClaimVolumeSource(
                claim_name=settings_dict["PVC_OUTPUT_NAME"]
            ),
        ),
    ]
    volume_mounts = [
        client.V1VolumeMount(
            name="data-volume",
            mount_path=settings_dict["MOUNT_PATH"],
            sub_path=settings_dict["SUB_PATH"],
        ),
        client.V1VolumeMount(
            name="data-output-volume", mount_path=settings_dict["OUTPUT_PATH"]
        ),
    ]
    logger.info(f"Using PVC: {settings_dict['PVC_NAME']}")
    logger.info(f"Using PVC OUTPOUT: {settings_dict['PVC_OUTPUT_NAME']}")

    # Define job container with debugging
    debug_script = f"""
set -e
echo ""
echo "Attempting to install coreutils for unbuffered output support..."
# Temporarily disable exit-on-error for package installation attempts
set +e
# Try to install coreutils (which includes stdbuf) - works on Debian/Ubuntu
if command -v apt-get &> /dev/null; then
    apt-get update -qq 2>&1 && apt-get install -y -qq coreutils 2>&1
    if [ $? -eq 0 ]; then
        echo "Installed coreutils via apt-get"
    else
        echo "Failed to install coreutils via apt-get (may already be installed or no permissions)"
    fi
# Try Alpine Linux package manager
elif command -v apk &> /dev/null; then
    apk add --no-cache coreutils 2>&1
    if [ $? -eq 0 ]; then
        echo "Installed coreutils via apk"
    else
        echo "Failed to install coreutils via apk (may already be installed or no permissions)"
    fi
# Try Red Hat/CentOS package manager
elif command -v yum &> /dev/null; then
    yum install -y -q coreutils 2>&1
    if [ $? -eq 0 ]; then
        echo "Installed coreutils via yum"
    else
        echo "Failed to install coreutils via yum (may already be installed or no permissions)"
    fi
else
    echo "No supported package manager found for coreutils installation"
fi
# Re-enable exit-on-error for the main command
set -e

echo ""
echo "Running LidarDataManager with args: {' '.join(full_cli_args)}"
# Change to the directory containing the metacloud file before running LidarDataManager
# This ensures relative paths in the metacloud file work correctly
if [[ "$INPUT_FILE" == *.metacloud ]]; then
    METACLOUD_DIR=$(dirname "$INPUT_FILE")
    echo "Changing working directory to: $METACLOUD_DIR"
    cd "$METACLOUD_DIR" || echo "Cannot cd to metacloud directory"
    echo "New working directory: $(pwd)"
fi

# Try different methods for unbuffered output in order of preference
if command -v stdbuf &> /dev/null; then
    echo "Using stdbuf for unbuffered output"
    stdbuf -o0 -e0 /lidarDataManager {' '.join(full_cli_args)}
elif command -v script &> /dev/null; then
    echo "Using script command for unbuffered output"
    # Use script with -q (quiet) -e (return exit code) -f (flush output) -c (command)
    script -q -e -f -c "/lidarDataManager {' '.join(full_cli_args)}" /dev/null
else
    echo "No unbuffering tool available, running directly (output may be buffered)"
    /lidarDataManager {' '.join(full_cli_args)}
fi
"""

    container = client.V1Container(
        name="lidar-container",
        image=container_image,
        command=["/bin/bash", "-c"],
        args=[debug_script],
        volume_mounts=volume_mounts,
        env=[
            # Force unbuffered output for real-time log streaming
            client.V1EnvVar(name="PYTHONUNBUFFERED", value="1"),
            client.V1EnvVar(name="GLOG_logtostderr", value="1"),
            client.V1EnvVar(name="GLOG_v", value="1"),
            # Disable output buffering
            client.V1EnvVar(name="UNBUFFERED", value="1"),
        ],
        # Enable TTY to help with unbuffered output
        tty=False,  # Keep False to avoid binary/control character issues in logs
        stdin=False,
        resources=client.V1ResourceRequirements(
            requests={
                "cpu": os.getenv("LIDAR_JOB_CPU_REQUEST", "500m"),
                "memory": os.getenv(
                    "LIDAR_JOB_MEMORY_REQUEST", "2Gi"
                ),  # Increased default
            },
            limits={
                "cpu": os.getenv("LIDAR_JOB_CPU_LIMIT", "2"),
                "memory": os.getenv(
                    "LIDAR_JOB_MEMORY_LIMIT", "8Gi"
                ),  # Increased default
            },
        ),
    )
    # Create labels based on environment
    annotations = {}
    app_name = "addlidar"
    environment = settings_dict["ENVIRONMENT"]

    if environment == "production":
        app_name = "addlidar-prod"
    else:  # development or any other environment
        app_name = "addlidar-dev"

    annotations["argocd.argoproj.io/instance"] = app_name
    # Prevent ArgoCD from pruning dynamically created jobs
    annotations["argocd.argoproj.io/sync-options"] = "Prune=false"

    # Get node scheduling configuration using utility function
    tolerations_config, node_selector_config = get_node_scheduling_config()

    # Convert tolerations from dict format to Kubernetes client objects if needed
    tolerations = []
    if tolerations_config:
        for tol in tolerations_config:
            tolerations.append(
                client.V1Toleration(
                    key=tol["key"],
                    value=tol["value"],
                    operator=tol["operator"],
                    effect=tol["effect"],
                )
            )
        logger.info(f"Added tolerations for node scheduling: {tolerations_config}")

    # Use node selector as-is if provided
    node_selector = node_selector_config if node_selector_config else {}
    if node_selector:
        logger.info(f"Added node selector: {node_selector}")

    # Define job with labels matching existing deployment pattern
    job_labels = {
        "app": app_name,
        "argocd.argoproj.io/instance": app_name,  # This is the key label for ArgoCD tracking
        "addlidar.io/job-type": "lidar-processing",
    }

    job = client.V1Job(
        api_version="batch/v1",
        kind="Job",
        metadata=client.V1ObjectMeta(
            name=job_name,
            namespace=settings_dict["NAMESPACE"],
            labels=job_labels,
            annotations=annotations,
        ),
        spec=client.V1JobSpec(
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels=job_labels),
                spec=client.V1PodSpec(
                    containers=[container],
                    volumes=volumes,
                    restart_policy="Never",
                    tolerations=tolerations if tolerations else None,
                    node_selector=node_selector if node_selector else None,
                ),
            ),
            backoff_limit=3,  # Retry up to 3 times on failure
            ttl_seconds_after_finished=86400,  # Keep job pods for 24 hours for log inspection
        ),
    )

    # Create the job
    batch_v1.create_namespaced_job(namespace=settings_dict["NAMESPACE"], body=job)
    logger.info(f"Created job {job_name}")
    return job_name


def create_k8s_job(job_name: str, cli_args: Optional[List[str]]) -> None:
    """
    Create a Kubernetes job that runs a simple hello world command.

    Args:
        job_name: Name of the job to create

    Returns:
        Tuple[str, int]: The output (stdout or stderr) and exit code
    """
    # settings = get_settings()

    try:
        # Generate a unique filename for output
        unique_filename = f"output_{uuid.uuid4().hex}.bin"
        generate_k8s_addlidarmanager_job(job_name, unique_filename, cli_args)
        update_job_statuses(
            job_name,
            JobStatus(
                job_name=job_name,
                status="Created",
                created_at=datetime.now(),
                message="Job is created",
                output_path=unique_filename,
                cli_args=cli_args,
            ),
            asyncio.get_event_loop(),
        )
        logger.info(
            f"Created job {job_name}, output will be saved to {unique_filename}, cli_args: {cli_args}"
        )
        logger.info(f"Created job {job_name}")
        return job_name
    except Exception as e:
        error_msg = f"Failed to create or run job {job_name}: {str(e)}"
        logger.error(error_msg)
        return error_msg, 1
