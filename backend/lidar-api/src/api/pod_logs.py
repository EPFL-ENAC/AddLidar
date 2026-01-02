"""
API Routes for Pod Logs

Provides endpoints to view captured pod logs.
"""

import os
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pod-logs", tags=["pod-logs"])

LOG_STORAGE_PATH = os.getenv("POD_LOG_STORAGE_PATH", "/data/pod-logs")


class LogFileInfo(BaseModel):
    """Information about a captured log file."""

    filename: str
    pod_name: str
    capture_time: str
    size_bytes: int
    path: str


@router.get("/", response_model=List[LogFileInfo])
async def list_pod_logs(
    pod_name_filter: Optional[str] = Query(None, description="Filter by pod name"),
    limit: int = Query(100, description="Maximum number of logs to return"),
):
    """
    List all captured pod logs.

    Args:
        pod_name_filter: Optional filter to only show logs for specific pod name pattern
        limit: Maximum number of logs to return

    Returns:
        List of log file information
    """
    try:
        log_path = Path(LOG_STORAGE_PATH)

        if not log_path.exists():
            return []

        log_files = []
        for log_file in sorted(log_path.glob("*.log"), key=lambda x: x.stat().st_mtime, reverse=True):
            # Apply pod name filter if provided
            if pod_name_filter and pod_name_filter not in log_file.stem:
                continue

            # Extract pod name from filename (format: podname_timestamp.log)
            parts = log_file.stem.rsplit("_", 2)
            pod_name = "_".join(parts[:-2]) if len(parts) > 2 else parts[0]
            capture_time = parts[-2] + "_" + parts[-1] if len(parts) > 2 else "unknown"

            log_files.append(
                LogFileInfo(
                    filename=log_file.name,
                    pod_name=pod_name,
                    capture_time=capture_time,
                    size_bytes=log_file.stat().st_size,
                    path=str(log_file),
                )
            )

            if len(log_files) >= limit:
                break

        return log_files

    except Exception as e:
        logger.error(f"Error listing pod logs: {e}")
        raise HTTPException(status_code=500, detail=f"Error listing pod logs: {str(e)}")


@router.get("/{filename}")
async def get_pod_log(filename: str):
    """
    Get the content of a specific pod log file.

    Args:
        filename: Name of the log file

    Returns:
        Log file content as plain text
    """
    try:
        log_path = Path(LOG_STORAGE_PATH) / filename

        if not log_path.exists() or not log_path.is_file():
            raise HTTPException(status_code=404, detail="Log file not found")

        # Security check: ensure the file is within LOG_STORAGE_PATH
        if not str(log_path.resolve()).startswith(str(Path(LOG_STORAGE_PATH).resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        return FileResponse(
            path=log_path,
            media_type="text/plain",
            filename=filename,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving pod log {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving pod log: {str(e)}")


@router.delete("/{filename}")
async def delete_pod_log(filename: str):
    """
    Delete a specific pod log file.

    Args:
        filename: Name of the log file to delete

    Returns:
        Success message
    """
    try:
        log_path = Path(LOG_STORAGE_PATH) / filename

        if not log_path.exists() or not log_path.is_file():
            raise HTTPException(status_code=404, detail="Log file not found")

        # Security check: ensure the file is within LOG_STORAGE_PATH
        if not str(log_path.resolve()).startswith(str(Path(LOG_STORAGE_PATH).resolve())):
            raise HTTPException(status_code=403, detail="Access denied")

        log_path.unlink()
        logger.info(f"Deleted pod log file: {filename}")

        return JSONResponse(content={"message": f"Log file {filename} deleted successfully"})

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting pod log {filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting pod log: {str(e)}")


@router.get("/search/by-job/{job_name}")
async def search_logs_by_job(job_name: str):
    """
    Search for pod logs related to a specific job name.

    Args:
        job_name: Name of the job to search for

    Returns:
        List of matching log files
    """
    return await list_pod_logs(pod_name_filter=job_name, limit=100)
