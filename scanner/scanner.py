#!/usr/bin/env python3
# /// script
# dependencies = [
#   "kubernetes",
#   "pydantic",
#   "jinja2",
#   "requests",
# ]
# ///
"""
LiDAR Archive Scanner and Job Enqueuer

This script scans directories containing LiDAR data and queues Kubernetes jobs
to create compressed archives of changed directories.
"""

import os
import json
import subprocess
import time
import uuid
import logging
import sys
import argparse
import hashlib
from typing import Dict, List, Optional, Tuple, Set
from datetime import datetime

try:
    # Import dependencies
    from kubernetes import client, config
    import jinja2
    import requests
except ImportError:
    print(
        "Error: required modules not found. Run this script with 'uv run' to auto-install dependencies."
    )
    sys.exit(1)

# Initial logger setup with default level (will be updated in main)
logging.basicConfig(
    level=logging.INFO,  # Default level, will be overridden in main()
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("scanner.py")

# Constants will be set in main() from arguments
ORIG: str = ""
ZIP: str = ""
# Default PVC for FTS AddLidar, can be overridden by command line argument
FTS_ADDLIDAR_PVC: str = ""
# Default backend URL, can be overridden by command line argument
BACKEND_URL: str = ""
# We'll store parsed args globally so they can be accessed from other functions
args = None


# API Client Functions
def api_get_folder_state(folder_key: str) -> Optional[Dict]:
    """Get folder state from API by folder key"""
    try:
        url = f"{BACKEND_URL}/sqlite/folder_state/{folder_key}"
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()
        # Return first record if available
        if data.get("data") and len(data["data"]) > 0:
            return data["data"][0]
        return None
    except Exception as e:
        logger.error(f"Error fetching folder state for {folder_key}: {e}")
        return None


def api_check_mission_exists(mission_key: str) -> bool:
    """Check if mission exists in folder_state via API"""
    try:
        url = f"{BACKEND_URL}/sqlite/folder_state/mission/{mission_key}"
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        data = response.json()
        return data.get("count", 0) > 0
    except Exception as e:
        logger.error(f"Error checking mission existence for {mission_key}: {e}")
        return False


def api_get_potree_metacloud_state(mission_key: str) -> Optional[Dict]:
    """Get potree metacloud state from API by mission key"""
    try:
        url = f"{BACKEND_URL}/sqlite/potree_metacloud_state/{mission_key}"
        response = requests.get(url, timeout=30)
        if response.status_code == 404:
            return None
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching potree metacloud state for {mission_key}: {e}")
        return None


def api_create_folder_state(
    folder_key: str, mission_key: str, fp: str, size: int, count: int, output_path: str
) -> bool:
    """Create or update folder state via API"""
    try:
        # First try to update existing record via API
        url = f"{BACKEND_URL}/sqlite/folder_state/{folder_key}"
        payload = {"fingerprint": fp, "processing_status": "pending"}
        response = requests.put(url, json=payload, timeout=30)

        if response.status_code == 404:
            # Record doesn't exist - create it via API
            logger.info(f"Creating new folder state record via API for {folder_key}")
            create_url = f"{BACKEND_URL}/sqlite/folder_state"
            create_payload = {
                "folder_key": folder_key,
                "mission_key": mission_key,
                "fingerprint": fp,
                "size_kb": size,
                "file_count": count,
                "output_path": output_path,
                "processing_status": "pending",
            }
            create_response = requests.post(create_url, json=create_payload, timeout=30)
            create_response.raise_for_status()
            return True

        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error creating/updating folder state for {folder_key}: {e}")
        return False


def api_create_potree_metacloud_state(
    mission_key: str,
    fp: str,
    output_path: str,
) -> bool:
    """Create or update potree metacloud state via API"""
    try:
        # Try to update existing record via API
        url = f"{BACKEND_URL}/sqlite/potree_metacloud_state/{mission_key}"
        payload = {"fingerprint": fp, "processing_status": "pending"}
        response = requests.put(url, json=payload, timeout=30)

        if response.status_code == 404:
            # Record doesn't exist - create it via API
            logger.info(
                f"Creating new potree metacloud state record via API for {mission_key}"
            )
            create_url = f"{BACKEND_URL}/sqlite/potree_metacloud_state"
            create_payload = {
                "mission_key": mission_key,
                "fingerprint": fp,
                "output_path": output_path,
                "processing_status": "pending",
            }
            create_response = requests.post(create_url, json=create_payload, timeout=30)
            create_response.raise_for_status()
            return True

        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(
            f"Error creating/updating potree metacloud state for {mission_key}: {e}"
        )
        return False


def api_update_potree_metacloud_last_checked(mission_key: str) -> bool:
    """Update only the last_checked timestamp for potree metacloud state"""
    try:
        url = f"{BACKEND_URL}/sqlite/potree_metacloud_state/{mission_key}/last_checked"
        response = requests.patch(url, timeout=30)
        if response.status_code == 404:
            logger.warning(
                f"Potree metacloud state not found for mission {mission_key}"
            )
            return False
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(
            f"Error updating last_checked for potree metacloud state {mission_key}: {e}"
        )
        return False


def api_update_folder_last_checked(folder_key: str) -> bool:
    """Update only the last_checked timestamp for folder state"""
    try:
        url = f"{BACKEND_URL}/sqlite/folder_state/{folder_key}/last_checked"
        response = requests.patch(url, timeout=30)
        if response.status_code == 404:
            logger.warning(f"Folder state not found for {folder_key}")
            return False
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error updating last_checked for folder {folder_key}: {e}")
        return False


def fingerprint_file(file_path: str) -> str:
    """
    Generate a unique fingerprint for a single file.

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 hash representing the file content
    """
    import hashlib

    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read in chunks for memory efficiency
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate fingerprint for file {file_path}: {e}")
        raise


def fingerprint(path: str) -> str:
    """
    Generate a unique fingerprint for a directory based on file attributes.

    Args:
        path: Directory path to fingerprint

    Returns:
        SHA-256 hash representing the directory content state
    """
    import hashlib
    import os

    try:
        # List to store file information tuples (relative_path, size_bytes, mod_time)
        file_info = []

        # Walk through the directory tree
        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                # Get relative path from the base directory
                rel_path = os.path.relpath(full_path, path)

                # Get file stats
                stat_result = os.stat(full_path, follow_symlinks=False)
                size_bytes = stat_result.st_size
                mod_time = stat_result.st_mtime

                # Store information as a tuple
                file_info.append((rel_path, size_bytes, mod_time))

        # Sort the list to ensure consistent ordering
        file_info.sort()

        # Create a hash object
        hasher = hashlib.sha256()

        # Add each file's information to the hash
        for rel_path, size_bytes, mod_time in file_info:
            # Format: relative_path|size|modification_time
            file_data = f"{rel_path}|{size_bytes}|{mod_time}\n".encode("utf-8")
            hasher.update(file_data)

        # Return the hexadecimal digest
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate fingerprint for {path}: {e}")
        raise


def get_directory_stats(path: str) -> Tuple[str, int, int]:
    """
    Get directory statistics: fingerprint, size in KB, and file count.

    Args:
        path: Path to directory

    Returns:
        Tuple containing (fingerprint, size_kb, file_count)
    """
    fp = fingerprint(path)
    try:
        size = int(subprocess.check_output(["du", "-sk", path]).split()[0])
        count = int(
            subprocess.check_output(
                ["bash", "-c", f"find '{path}' -type f | wc -l"]
            ).strip()
        )
        return fp, size, count
    except subprocess.SubprocessError as e:
        logger.error(f"Failed to get stats for directory {path}: {e}")
        raise


def scan_for_metacloud_files(dry_run: bool = False) -> List[List[str]]:
    """
    Scan directories for .metacloud files and track changes.

    Args:
        dry_run: Whether to perform a dry run without modifying the database

    Returns:
        List of lists containing [mission_key, metacloud_path, fingerprint] that have changed
    """
    global ORIG
    metacloud_changes: List[List[str]] = []
    current_time = int(time.time())

    # First, list all level1 directories (missions)
    for level1 in os.listdir(ORIG):
        p1 = os.path.join(ORIG, level1)
        if not os.path.isdir(p1):
            continue

        # Look for .metacloud file in the mission directory
        metacloud_file = None
        for file in os.listdir(p1):
            if file.endswith(".metacloud"):
                metacloud_file = os.path.join(p1, file)
                break

        if not metacloud_file:
            logger.info(f"No .metacloud file found in mission {level1}")
            continue

        # Get fingerprint of the metacloud file
        try:
            metacloud_fp = fingerprint_file(metacloud_file)
            logger.info(
                f"Found .metacloud file in {level1}, fingerprint: {metacloud_fp}"
            )

            # Check if the metacloud file has changed or needs reprocessing
            row = api_get_potree_metacloud_state(level1)

            # Check if metacloud file needs processing:
            # 1. New file (not in database)
            # 2. Fingerprint has changed
            # 3. Previous processing failed or is still pending
            needs_processing = False
            if not row:
                logger.info(f"New .metacloud file detected for mission {level1}")
                needs_processing = True
            elif row.get("fp") != metacloud_fp:
                logger.info(
                    f"Fingerprint change detected in .metacloud file for mission {level1}"
                )
                needs_processing = True
            elif row.get("processing_status") in ("pending", "failed", None):
                logger.info(
                    f"Incomplete processing detected for .metacloud file in mission {level1} (status: {row.get('processing_status')})"
                )
                needs_processing = True

            if needs_processing:
                logger.info(
                    f"Adding .metacloud file for mission {level1} to processing queue"
                )
                metacloud_changes.append([level1, metacloud_file, metacloud_fp])

                if not dry_run:
                    output_path = os.path.join(os.path.dirname(ZIP), "Potree", level1)

                    api_create_potree_metacloud_state(level1, metacloud_fp, output_path)
            else:
                # Just update the last_checked timestamp for successful completions
                if not dry_run:
                    api_update_potree_metacloud_last_checked(level1)
                logger.debug(
                    f"No processing needed for .metacloud file in mission {level1} (status: {row.get('processing_status') if row else 'N/A'})"
                )

        except Exception as e:
            logger.error(f"Error processing metacloud file in {level1}: {e}")

    return metacloud_changes


def collect_changed_folders(dry_run: bool = False) -> List[List[str]]:
    """
    Scan directories and collect paths of changed folders without immediately queueing jobs.

    Args:
        dry_run: Whether to perform a dry run without modifying the database

    Returns:
        List of relative paths to folders that have changed
    """
    global ORIG
    changed_folders: List[List[str]] = []

    for level1 in os.listdir(ORIG):
        p1 = os.path.join(ORIG, level1)
        if not os.path.isdir(p1):
            continue

        for level2 in os.listdir(p1):
            rel = os.path.join(level1, level2)
            src = os.path.join(ORIG, rel)
            if not os.path.isdir(src):
                continue

            try:
                logger.info(f"Processing directory: {rel}")
                fp, size, count = get_directory_stats(src)
                logger.info(f"Fingerprint: {fp}, Size: {size} KB, File Count: {count}")

                row = api_get_folder_state(rel)

                # Check if folder needs processing:
                # 1. New folder (not in database)
                # 2. Fingerprint has changed
                # 3. Previous processing failed or is still pending
                needs_processing = False
                if not row:
                    logger.info(f"New folder detected: {rel}")
                    needs_processing = True
                elif row.get("fp") != fp:
                    logger.info(f"Fingerprint change detected in {rel}")
                    needs_processing = True
                elif row.get("processing_status") in ("pending", "failed", None):
                    logger.info(
                        f"Incomplete processing detected in {rel} (status: {row.get('processing_status')})"
                    )
                    needs_processing = True

                if needs_processing:
                    logger.info(f"Adding {rel} to processing queue")
                    changed_folders.append([rel, fp])

                    if not dry_run:
                        api_create_folder_state(
                            rel,
                            level1,
                            fp,
                            size,
                            count,
                            os.path.join(ZIP, f"{rel}.tar.gz"),
                        )
                else:
                    # Just update the last_checked timestamp for successful completions
                    if not dry_run:
                        answer = api_update_folder_last_checked(rel)
                        logger.debug(f"Updated last_checked for {rel}: {answer}")
                    logger.debug(
                        f"No processing needed for {rel} (status: {row.get('processing_status') if row else 'N/A'})"
                    )

            except Exception as e:
                logger.error(f"Error processing directory {rel}: {e}")

    return changed_folders


def queue_potree_conversion_jobs(
    metacloud_files: List[List[str]], export_only: bool = False
) -> Optional[int]:
    """
    Create a Kubernetes batch job for Potree conversion of metacloud files using a template.

    Args:
        metacloud_files: List containing [mission_key, metacloud_path, fingerprint] lists
        export_only: Whether to only export the job YAML without creating it

    Returns:
        Optional[int]: Number of jobs created (1 if batch job created) or None if no action was taken
    """
    global ORIG, ZIP, FTS_ADDLIDAR_PVC, BACKEND_URL, args

    if not metacloud_files:
        logger.info("No metacloud files to process, skipping job creation")
        return None

    try:
        # Load Jinja2 template
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "job-batch-potree-converter.template.yaml",
        )

        if not os.path.exists(template_path):
            logger.error(f"Potree template file not found at {template_path}")
            return None

        with open(template_path, "r") as f:
            template_content = f.read()

        # Setup Jinja2 environment
        template = jinja2.Template(template_content)

        # Generate timestamp for unique job name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        # Prepare template context
        parallelism = min(
            len(metacloud_files), 4
        )  # Limit parallelism based on number of files

        context = {
            "timestamp": timestamp,
            "metacloud_files": metacloud_files,
            "parallelism": parallelism,
            "fts_addlidar_pvc_name": FTS_ADDLIDAR_PVC,
            "backend_url": BACKEND_URL,
            "potree_converter_image_registry": os.environ.get(
                "POTREE_CONVERTER_IMAGE_REGISTRY"
            ),
            "potree_converter_image_name": os.environ.get(
                "POTREE_CONVERTER_IMAGE_NAME"
            ),
            "potree_converter_image_tag": os.environ.get("POTREE_CONVERTER_IMAGE_TAG"),
            "potree_converter_image_sha256": os.environ.get(
                "POTREE_CONVERTER_IMAGE_SHA256"
            ),
        }

        # Render the template
        job_yaml = template.render(**context)

        if export_only:
            print(job_yaml)
            logger.info(
                f"Printed batch Potree job YAML for {len(metacloud_files)} metacloud files"
            )
            return 1

        # Create job from YAML
        import yaml
        from kubernetes import utils

        job_dict = yaml.safe_load(job_yaml)
        try:
            result = utils.create_from_dict(client.ApiClient(), job_dict, True)
            job_name = job_dict["metadata"]["name"]
            logger.info(
                f"Created batch Potree conversion job '{job_name}' for {len(metacloud_files)} metacloud files"
            )
            logger.debug(f"Job creation result: {result}")
            return 1
        except Exception as api_ex:
            logger.error(f"Failed to create Kubernetes batch job via API: {api_ex}")
            return None

    except Exception as e:
        logger.error(f"Failed to create Potree conversion batch job: {e}")
        return None


def queue_batch_zip_job(
    folders: List[List[str]], export_only: bool = False
) -> Optional[int]:
    """
    Create a single batch Kubernetes job to process multiple folders.

    Args:
        folders: List of relative folder paths to archive with their fingerprints [rel, fp]
        export_only: Whether to only export the job YAML without creating it

    Returns:
        Optional[int]: Number of folders processed or None if no action was taken
    """
    global ORIG, ZIP, FTS_ADDLIDAR_PVC, BACKEND_URL, args

    if not folders:
        logger.info("No folders to process, skipping batch job creation")
        return

    # Generate timestamp for unique job name
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    try:
        # Load Jinja2 template
        template_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "job-batch-compression.template.yaml",
        )

        if not os.path.exists(template_path):
            logger.error(f"Template file not found at {template_path}")
            return

        with open(template_path, "r") as f:
            template_content = f.read()

        # Setup Jinja2 environment
        template = jinja2.Template(template_content)

        # Prepare template variables
        context = {
            "folders": folders,
            "timestamp": timestamp,
            "parallelism": args.parallelism,
            "orig_dir": ORIG,
            "zip_dir": ZIP,
            "fts_addlidar_pvc_name": FTS_ADDLIDAR_PVC,
            "backend_url": BACKEND_URL,
            "compression_image_registry": os.environ.get("COMPRESSION_IMAGE_REGISTRY"),
            "compression_image_name": os.environ.get("COMPRESSION_IMAGE_NAME"),
            "compression_image_tag": os.environ.get("COMPRESSION_IMAGE_TAG"),
            "compression_image_sha256": os.environ.get("COMPRESSION_IMAGE_SHA256"),
        }

        # Render the template
        job_yaml = template.render(**context)

        if export_only:
            print(job_yaml)
            logger.info(f"Printed batch job YAML for {len(folders)} folders")
            return

        # Create job from YAML
        import yaml
        from kubernetes import utils

        job_dict = yaml.safe_load(job_yaml)
        try:
            result = utils.create_from_dict(client.ApiClient(), job_dict, True)
            job_name = job_dict["metadata"]["name"]
            logger.info(f"Created batch job '{job_name}' for {len(folders)} folders")
            logger.debug(f"Job creation result: {result}")
            return len(folders)
        except Exception as api_ex:
            logger.error(f"Failed to create Kubernetes job via API: {api_ex}")
            raise
    except Exception as e:
        logger.error(f"Failed to create batch job: {e}")
        raise


def main() -> None:
    """
    Main function to scan directories and enqueue archive jobs.
    """
    # Access global constants and args to modify them
    global ORIG, ZIP, FTS_ADDLIDAR_PVC, BACKEND_URL, args

    parser = argparse.ArgumentParser(
        description="LiDAR Archive Scanner and Job Enqueuer"
    )
    parser.add_argument(
        "--original-root",
        default="./original_root",
        help="Root directory containing original LiDAR data",
    )
    parser.add_argument(
        "--zip-root",
        default="./zip_root",
        help="Root directory where compressed archives will be stored",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set logging level (default: INFO)",
    )

    parser.add_argument(
        "--fts-addlidar-pvc",
        default="fts-addlidar",
        help="PVC name for the FTS AddLidar (default: 'fts-addlidar')",
    )
    parser.add_argument(
        "--backend-url",
        default="http://backend-internal",
        help="Backend API URL for database updates (default: 'http://backend-internal')",
    )
    # parser.add_argument(
    #     "--execution-env",
    #     choices=["local", "docker", "kubernetes", "kube", "batch"],
    #     default="local",
    #     help="Execution environment for archive jobs (default: local)"
    # )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check for changes without modifying database or queueing jobs",
    )
    parser.add_argument(
        "--export-only",
        action="store_true",
        help="Print job YAMLs/commands instead of creating them",
    )
    parser.add_argument(
        "--max-jobs",
        type=int,
        default=0,
        help="Stop after the specified number of archive jobs have been queued (0 for unlimited)",
    )
    parser.add_argument(
        "--parallelism",
        type=int,
        default=4,
        help="Number of parallel jobs to run in batch mode",
    )
    args = parser.parse_args()

    # Set logging level from command line argument
    log_level = args.log_level.upper()
    logger.setLevel(getattr(logging, log_level))
    logger.info(f"Log level set to: {log_level}")

    # Assign parsed arguments to global constants
    ORIG = args.original_root
    ZIP = args.zip_root
    FTS_ADDLIDAR_PVC = args.fts_addlidar_pvc
    BACKEND_URL = args.backend_url
    execution_env = "batch"

    dry_run: bool = args.dry_run
    export_only: bool = args.export_only

    # Configuration validation moved here
    if not os.path.isdir(ORIG):
        logger.warning(
            f"Original root directory '{ORIG}' does not exist, creating it..."
        )
        os.makedirs(ORIG, exist_ok=True)

    if not os.path.isdir(ZIP):
        logger.warning(f"Zip root directory '{ZIP}' does not exist, creating it...")
        os.makedirs(ZIP, exist_ok=True)

    logger.info(f"Starting scan: ORIG='{ORIG}', ZIP='{ZIP}'")
    logger.info(
        f"Options: execution_env='{execution_env}', log_level='{log_level}', "
        f"dry-run={dry_run}, export_only={export_only}"
    )

    # Load Kube config if using kubernetes modes
    if execution_env in ("kubernetes", "kube", "batch"):
        try:
            config.load_incluster_config()
            logger.info("Loaded Kubernetes in-cluster config")
        except config.ConfigException:
            logger.warning("Failed to load in-cluster config, trying local kube config")
            try:
                config.load_kube_config()
                logger.info("Loaded local Kubernetes config")
            except Exception as e:
                logger.error(f"Failed to load any Kubernetes config: {e}")
                # Exit if Kubernetes mode is requested but config loading fails
                sys.exit(1)

    logger.info(f"Scanner initialized. Using backend at {BACKEND_URL}")

    # Process based on execution environment
    # Collect all changed folders first
    changed_folders = collect_changed_folders(dry_run)

    # Limit folders if max_jobs is specified
    max_jobs = args.max_jobs
    length_changed_folders = len(changed_folders)
    if max_jobs > 0 and length_changed_folders > max_jobs:
        logger.info(
            f"Limiting to {max_jobs} out of {length_changed_folders} changed folders"
        )
        changed_folders = changed_folders[:max_jobs]

    # Create a single batch job for all folders
    if changed_folders:
        logger.info(f"Creating batch job for {length_changed_folders} changed folders")
        processed_count = queue_batch_zip_job(changed_folders, export_only)
        if processed_count:
            logger.info(f"Successfully created {processed_count} jobs")
    else:
        logger.info("No changes detected, no batch job needed")

    # Process metacloud files if requested
    metacloud_count = 0
    logger.info("Scanning for .metacloud files...")
    metacloud_changes = scan_for_metacloud_files(dry_run)
    metacloud_count = len(metacloud_changes)

    if metacloud_changes:
        logger.info(f"Found {metacloud_count} .metacloud files to process")
        # Use max_jobs to limit metacloud files as well
        if max_jobs > 0 and metacloud_count > max_jobs:
            logger.info(
                f"Limiting to {max_jobs} out of {metacloud_count} metacloud files"
            )
            metacloud_changes = metacloud_changes[:max_jobs]
            metacloud_count = max_jobs

        potree_job_count = queue_potree_conversion_jobs(metacloud_changes, export_only)
        if potree_job_count:
            logger.info(
                f"Successfully created potree conversion job for {metacloud_count} files"
            )

    # Update completion message to include metacloud information
    logger.info(
        f"Scan completed: detected {length_changed_folders} folder changes"
        + (
            f" and {metacloud_count} metacloud changes"
            if metacloud_count > 0  # Changed from args.process_metacloud
            else ""
        )
    )


if __name__ == "__main__":
    main()
