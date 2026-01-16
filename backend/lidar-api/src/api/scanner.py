from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Optional
from datetime import datetime
from kubernetes import client
from enacit4r_auth.services.auth import User

from src.config.settings import settings
from src.services import scanner_utils
from src.services.auth import kc_service

router = APIRouter(prefix="/scanner", tags=["scanner"])
logger = logging.getLogger("uvicorn")


@router.post("/trigger")
async def trigger_scanner(background_tasks: BackgroundTasks, user: User = Depends(kc_service.get_user_info())):
    """
    Trigger the scanner job to process new LiDAR data.

    This endpoint creates a one-off Kubernetes Job that runs the scanner script,
    which will:
    - Scan for changed directories and queue compression jobs
    - Scan for .metacloud files and queue Potree conversion jobs
    - Copy footprint.geojson files
    - Update mission protection status based on .password files

    Returns:
        dict: Job name and status information
    """
    logger.info(f"Scanner trigger requested by user: {user.username} (id: {user.id})")

    try:
        namespace = settings.effective_namespace

        # Check if scanner is already running
        if scanner_utils.is_scanner_running(namespace):
            return JSONResponse(
                status_code=409,
                content={
                    "status": "error",
                    "message": "Scanner is already running. Please wait for the current job to complete.",
                },
            )

        batch_v1 = client.BatchV1Api()

        # Generate unique job name with timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        job_name = f"scanner-manual-{timestamp}"

        # Create the job using scanner_utils
        job_name = scanner_utils.create_scanner_job(
            namespace=namespace,
            job_name=job_name,
        )

        logger.info(f"Scanner job {job_name} created successfully")

        return {
            "status": "success",
            "message": "Scanner job triggered successfully",
            "job_name": job_name,
            "namespace": namespace,
        }

    except Exception as e:
        logger.error(f"Error triggering scanner: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to trigger scanner: {str(e)}",
            },
        )


@router.get("/status")
async def get_scanner_status(user: User = Depends(kc_service.get_user_info())):
    """
    Check if a scanner job is currently running.

    Returns:
        dict: Scanner status with information about active jobs
    """
    try:
        namespace = settings.effective_namespace
        jobs = scanner_utils.list_scanner_jobs(namespace=namespace, job_type="scanner")

        # Check for running jobs
        running_jobs = [job for job in jobs if job.get("status") in ["Running", "Pending"]]

        return {
            "is_running": len(running_jobs) > 0,
            "running_jobs": running_jobs,
            "total_scanner_jobs": len(jobs),
        }

    except Exception as e:
        logger.error(f"Error getting scanner status: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get scanner status: {str(e)}",
            },
        )


@router.get("/jobs")
async def list_scanner_jobs(job_type: Optional[str] = None, limit: int = 50, user: User = Depends(kc_service.get_user_info())):
    """
    List scanner-related jobs (scanner, compression, potree-converter).

    Args:
        job_type: Optional filter by job type (scanner, compression, potree-converter)
        limit: Maximum number of jobs to return

    Returns:
        dict: List of jobs with their status
    """
    try:
        namespace = settings.effective_namespace
        jobs = scanner_utils.list_scanner_jobs(namespace=namespace, job_type=job_type, limit=limit)

        return {
            "status": "success",
            "count": len(jobs),
            "jobs": jobs,
        }

    except Exception as e:
        logger.error(f"Error listing scanner jobs: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to list scanner jobs: {str(e)}",
            },
        )


@router.get("/jobs/{job_name}")
async def get_scanner_job_status(job_name: str, user: User = Depends(kc_service.get_user_info())):
    """
    Get detailed status of a specific scanner-related job.

    Args:
        job_name: Name of the job

    Returns:
        dict: Detailed job status information
    """
    try:
        namespace = settings.effective_namespace
        job_info = scanner_utils.get_job_status(namespace=namespace, job_name=job_name)

        return {"status": "success", "job": job_info}

    except Exception as e:
        logger.error(f"Error getting job status for {job_name}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get job status: {str(e)}",
            },
        )


@router.get("/jobs/{job_name}/logs")
async def get_scanner_job_logs(job_name: str, tail_lines: int = 100, user: User = Depends(kc_service.get_user_info())):
    """
    Get logs from a specific scanner-related job.

    Args:
        job_name: Name of the job
        tail_lines: Number of lines to retrieve from the end (default: 100)

    Returns:
        dict: Logs from all pods in the job
    """
    try:
        namespace = settings.effective_namespace
        logs = scanner_utils.get_job_logs(namespace=namespace, job_name=job_name, tail_lines=tail_lines)

        return {"status": "success", "job_name": job_name, "logs": logs}

    except Exception as e:
        logger.error(f"Error getting logs for {job_name}: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Failed to get job logs: {str(e)}",
            },
        )
