"""
Scanner Job Management Utilities

Provides functions to trigger and monitor scanner-related Kubernetes jobs.
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException

logger = logging.getLogger("uvicorn")


def get_scanner_job_labels() -> Dict[str, str]:
    """Get labels used to identify scanner-related jobs."""
    return {"app": "scanner", "addlidar.io/managed-by": "addlidar"}


def create_scanner_job(namespace: str, job_name: Optional[str] = None, cronjob_name: str = "scanner") -> str:
    """
    Create a one-off scanner job from the existing CronJob template.

    This reads the CronJob configuration and creates a Job from its template,
    exactly like ArgoCD's "Create Job" functionality.

    Args:
        namespace: Kubernetes namespace
        job_name: Optional custom job name
        cronjob_name: Name of the CronJob to use as template (default: "scanner")

    Returns:
        Name of the created job
    """
    if not job_name:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        job_name = f"scanner-manual-{timestamp}"

    try:
        batch_v1 = client.BatchV1Api()

        # Read the existing CronJob
        cronjob = batch_v1.read_namespaced_cron_job(name=cronjob_name, namespace=namespace)

        # Extract the job template from the CronJob
        job_template = cronjob.spec.job_template

        # Create a new Job from the template
        job = client.V1Job(
            api_version="batch/v1",
            kind="Job",
            metadata=client.V1ObjectMeta(
                name=job_name,
                namespace=namespace,
                # Combine original labels with our tracking labels
                labels={
                    **(job_template.metadata.labels or {}),
                    **get_scanner_job_labels(),
                    "addlidar.io/job-type": "scanner",
                    "addlidar.io/triggered-by": "api",
                },
                annotations={
                    **(job_template.metadata.annotations or {}),
                    "addlidar.io/created-from": f"cronjob/{cronjob_name}",
                },
            ),
            spec=job_template.spec,
        )

        # Create the job
        batch_v1.create_namespaced_job(namespace=namespace, body=job)
        logger.info(f"Created scanner job '{job_name}' from CronJob '{cronjob_name}'")
        return job_name

    except ApiException as e:
        if e.status == 404:
            logger.error(f"CronJob '{cronjob_name}' not found in namespace '{namespace}'")
            raise ValueError(f"CronJob '{cronjob_name}' not found")
        logger.error(f"Failed to create scanner job: {e}")
        raise


def list_scanner_jobs(namespace: str, job_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict]:
    """
    List all scanner-related jobs (scanner, compression, potree-converter).

    Args:
        namespace: Kubernetes namespace
        job_type: Optional filter by job type (scanner, compression, potree-converter)
        limit: Optional maximum number of jobs to return

    Returns:
        List of job information dictionaries
    """
    try:
        batch_v1 = client.BatchV1Api()

        # Build label selector
        label_selector = "addlidar.io/managed-by=addlidar"
        if job_type:
            label_selector += f",addlidar.io/job-type={job_type}"

        jobs = batch_v1.list_namespaced_job(namespace=namespace, label_selector=label_selector)

        job_list = []
        for job in jobs.items:
            status = "Unknown"
            if job.status.succeeded:
                status = "Succeeded"
            elif job.status.failed:
                status = "Failed"
            elif job.status.active:
                status = "Running"
            else:
                status = "Pending"

            job_list.append(
                {
                    "name": job.metadata.name,
                    "type": job.metadata.labels.get("addlidar.io/job-type", "unknown"),
                    "status": status,
                    "created": job.metadata.creation_timestamp.isoformat() if job.metadata.creation_timestamp else None,
                    "active": job.status.active or 0,
                    "succeeded": job.status.succeeded or 0,
                    "failed": job.status.failed or 0,
                    "completion_time": job.status.completion_time.isoformat() if job.status.completion_time else None,
                }
            )

        sorted_jobs = sorted(job_list, key=lambda x: x["created"] or "", reverse=True)
        return sorted_jobs[:limit] if limit else sorted_jobs

    except ApiException as e:
        logger.error(f"Failed to list scanner jobs: {e}")
        raise


def get_job_logs(namespace: str, job_name: str, tail_lines: int = 100) -> Dict[str, str]:
    """
    Get logs from all pods of a job.

    Args:
        namespace: Kubernetes namespace
        job_name: Name of the job
        tail_lines: Number of lines to retrieve from the end

    Returns:
        Dictionary mapping pod names to their logs
    """
    try:
        core_v1 = client.CoreV1Api()

        # Find pods for this job
        pods = core_v1.list_namespaced_pod(namespace=namespace, label_selector=f"job-name={job_name}")

        if not pods.items:
            return {"error": f"No pods found for job {job_name}"}

        logs_dict = {}
        for pod in pods.items:
            pod_name = pod.metadata.name
            try:
                logs = core_v1.read_namespaced_pod_log(name=pod_name, namespace=namespace, tail_lines=tail_lines)
                logs_dict[pod_name] = logs
            except ApiException as e:
                logs_dict[pod_name] = f"Error retrieving logs: {e}"

        return logs_dict

    except ApiException as e:
        logger.error(f"Failed to get job logs: {e}")
        raise


def get_job_status(namespace: str, job_name: str) -> Dict:
    """
    Get detailed status of a specific job.

    Args:
        namespace: Kubernetes namespace
        job_name: Name of the job

    Returns:
        Job status dictionary
    """
    try:
        batch_v1 = client.BatchV1Api()
        job = batch_v1.read_namespaced_job(name=job_name, namespace=namespace)

        status = "Unknown"
        if job.status.succeeded:
            status = "Succeeded"
        elif job.status.failed:
            status = "Failed"
        elif job.status.active:
            status = "Running"
        else:
            status = "Pending"

        return {
            "name": job.metadata.name,
            "type": job.metadata.labels.get("addlidar.io/job-type", "unknown"),
            "status": status,
            "created": job.metadata.creation_timestamp.isoformat() if job.metadata.creation_timestamp else None,
            "start_time": job.status.start_time.isoformat() if job.status.start_time else None,
            "completion_time": job.status.completion_time.isoformat() if job.status.completion_time else None,
            "active": job.status.active or 0,
            "succeeded": job.status.succeeded or 0,
            "failed": job.status.failed or 0,
            "conditions": [
                {"type": condition.type, "status": condition.status, "reason": condition.reason, "message": condition.message}
                for condition in (job.status.conditions or [])
            ],
        }

    except ApiException as e:
        if e.status == 404:
            return {"error": f"Job {job_name} not found"}
        logger.error(f"Failed to get job status: {e}")
        raise


def is_scanner_running(namespace: str) -> bool:
    """
    Check if a scanner job is currently running.

    Args:
        namespace: Kubernetes namespace

    Returns:
        True if a scanner job is active
    """
    try:
        jobs = list_scanner_jobs(namespace, job_type="scanner")
        return any(job["status"] == "Running" for job in jobs)
    except Exception:
        return False
