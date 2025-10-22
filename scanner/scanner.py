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
import sys
import argparse
import logging
from datetime import datetime
from typing import List, Optional

# Add lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))

try:
    from kubernetes import config
    from lib.api_client import APIClient
    from lib.scanner import DirectoryScanner
    from lib.kubernetes_utils import (
        get_current_namespace,
        get_node_scheduling_config,
        get_resource_config_from_env,
        create_kubernetes_job,
    )
except ImportError:
    print(
        "Error: required modules not found. Run this script with 'uv run' to auto-install dependencies."
    )
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("scanner.py")


def get_argocd_app_name(namespace: str) -> str:
    """Determine the ArgoCD app name based on the namespace."""
    if namespace == "epfl-eso-addlidar-prod":
        return "addlidar-prod"
    else:
        return "addlidar-dev"


def queue_potree_conversion_jobs(
    metacloud_files: List[List[str]],
    api_client: APIClient,
    config_dict: dict,
    export_only: bool = False,
) -> Optional[int]:
    """Create a Kubernetes batch job for Potree conversion."""
    if not metacloud_files:
        logger.info("No metacloud files to process, skipping job creation")
        return None

    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "job-batch-potree-converter.template.yaml",
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    current_namespace = get_current_namespace()
    tolerations, node_selector = get_node_scheduling_config()
    resource_config = get_resource_config_from_env()

    # Get ArgoCD app name for annotations
    argocd_app_name = get_argocd_app_name(current_namespace)

    parallelism = min(len(metacloud_files), 4)

    context = {
        "timestamp": timestamp,
        "metacloud_files": metacloud_files,
        "parallelism": parallelism,
        "fts_addlidar_pvc_name": config_dict["fts_addlidar_pvc"],
        "backend_url": config_dict["backend_url"],
        "job_namespace": current_namespace,
        "argocd_app_name": argocd_app_name,
        "tolerations": tolerations,
        "node_selector": node_selector,
        **resource_config,
        "potree_converter_image_registry": os.environ.get(
            "POTREE_CONVERTER_IMAGE_REGISTRY"
        ),
        "potree_converter_image_name": os.environ.get("POTREE_CONVERTER_IMAGE_NAME"),
        "potree_converter_image_tag": os.environ.get("POTREE_CONVERTER_IMAGE_TAG"),
        "potree_converter_image_sha256": os.environ.get(
            "POTREE_CONVERTER_IMAGE_SHA256"
        ),
    }

    result = create_kubernetes_job(template_path, context, export_only)
    if result and not export_only:
        logger.info(
            f"Created batch Potree conversion job for {len(metacloud_files)} metacloud files"
        )
    return result


def queue_batch_zip_job(
    folders: List[List[str]],
    config_dict: dict,
    parallelism: int,
    export_only: bool = False,
) -> Optional[int]:
    """Create a single batch Kubernetes job to process multiple folders."""
    if not folders:
        logger.info("No folders to process, skipping batch job creation")
        return None

    template_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "job-batch-compression.template.yaml",
    )

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    current_namespace = get_current_namespace()
    tolerations, node_selector = get_node_scheduling_config()
    resource_config = get_resource_config_from_env()

    # Get ArgoCD app name for annotations
    argocd_app_name = get_argocd_app_name(current_namespace)

    context = {
        "folders": folders,
        "timestamp": timestamp,
        "parallelism": parallelism,
        "orig_dir": config_dict["original_root"],
        "zip_dir": config_dict["zip_root"],
        "fts_addlidar_pvc_name": config_dict["fts_addlidar_pvc"],
        "backend_url": config_dict["backend_url"],
        "argocd_app_name": argocd_app_name,
        "tolerations": tolerations,
        "node_selector": node_selector,
        "job_namespace": current_namespace,
        **resource_config,
        "compression_image_registry": os.environ.get("COMPRESSION_IMAGE_REGISTRY"),
        "compression_image_name": os.environ.get("COMPRESSION_IMAGE_NAME"),
        "compression_image_tag": os.environ.get("COMPRESSION_IMAGE_TAG"),
        "compression_image_sha256": os.environ.get("COMPRESSION_IMAGE_SHA256"),
    }

    result = create_kubernetes_job(template_path, context, export_only)
    if result and not export_only:
        logger.info(f"Created batch job for {len(folders)} folders")
    return len(folders) if result else None


def main() -> None:
    """Main function to scan directories and enqueue archive jobs."""
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
        help="Backend API URL for database updates",
    )
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
        help="Stop after the specified number of archive jobs (0 for unlimited)",
    )
    parser.add_argument(
        "--parallelism",
        type=int,
        default=4,
        help="Number of parallel jobs to run in batch mode",
    )

    args = parser.parse_args()

    # Set logging level
    log_level = args.log_level.upper()
    logger.setLevel(getattr(logging, log_level))
    logger.info(f"Log level set to: {log_level}")

    # Validate and create directories
    if not os.path.isdir(args.original_root):
        logger.warning(
            f"Original root directory '{args.original_root}' does not exist, creating it..."
        )
        os.makedirs(args.original_root, exist_ok=True)

    if not os.path.isdir(args.zip_root):
        logger.warning(
            f"Zip root directory '{args.zip_root}' does not exist, creating it..."
        )
        os.makedirs(args.zip_root, exist_ok=True)

    logger.info(f"Starting scan: ORIG='{args.original_root}', ZIP='{args.zip_root}'")

    # Load Kubernetes config
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
            sys.exit(1)

    # Initialize components
    api_client = APIClient(args.backend_url)
    scanner = DirectoryScanner(api_client, args.original_root, args.zip_root)

    config_dict = {
        "original_root": args.original_root,
        "zip_root": args.zip_root,
        "fts_addlidar_pvc": args.fts_addlidar_pvc,
        "backend_url": args.backend_url,
    }

    logger.info(f"Scanner initialized. Using backend at {args.backend_url}")

    # Copy footprint files before processing changes
    logger.info("Copying footprint.geojson files...")
    scanner.copy_footprint_files()

    # Scan for changed folders
    changed_folders = scanner.collect_changed_folders(args.dry_run)

    # Limit folders if max_jobs is specified
    length_changed_folders = len(changed_folders)
    if args.max_jobs > 0 and length_changed_folders > args.max_jobs:
        logger.info(
            f"Limiting to {args.max_jobs} out of {length_changed_folders} changed folders"
        )
        changed_folders = changed_folders[: args.max_jobs]

    # Create batch job for folders
    if changed_folders:
        logger.info(f"Creating batch job for {len(changed_folders)} changed folders")
        processed_count = queue_batch_zip_job(
            changed_folders, config_dict, args.parallelism, args.export_only
        )
        if processed_count:
            logger.info(f"Successfully created job for {processed_count} folders")
    else:
        logger.info("No changes detected, no batch job needed")

    # Process metacloud files
    logger.info("Scanning for .metacloud files...")
    metacloud_changes = scanner.scan_for_metacloud_files(args.dry_run)
    metacloud_count = len(metacloud_changes)

    if metacloud_changes:
        logger.info(f"Found {metacloud_count} .metacloud files to process")
        if args.max_jobs > 0 and metacloud_count > args.max_jobs:
            logger.info(
                f"Limiting to {args.max_jobs} out of {metacloud_count} metacloud files"
            )
            metacloud_changes = metacloud_changes[: args.max_jobs]
            metacloud_count = args.max_jobs

        potree_job_count = queue_potree_conversion_jobs(
            metacloud_changes, api_client, config_dict, args.export_only
        )
        if potree_job_count:
            logger.info(
                f"Successfully created potree conversion job for {metacloud_count} files"
            )

    # Summary
    logger.info(
        f"Scan completed: detected {length_changed_folders} folder changes"
        + (f" and {metacloud_count} metacloud changes" if metacloud_count > 0 else "")
    )


if __name__ == "__main__":
    main()
