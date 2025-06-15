"""
Command-line interface and main application logic.
"""

import argparse
import logging
import os
import sys

from kubernetes import client, config as k8s_config

from .api_client import APIClient
from .config import config, setup_logging
from .directory_scanner import DirectoryScanner
from .job_manager import JobManager

logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser"""
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
    return parser


def setup_kubernetes_config() -> bool:
    """Setup Kubernetes configuration"""
    try:
        k8s_config.load_incluster_config()
        logger.info("Loaded Kubernetes in-cluster config")
        return True
    except k8s_config.ConfigException:
        logger.warning("Failed to load in-cluster config, trying local kube config")
        try:
            k8s_config.load_kube_config()
            logger.info("Loaded local Kubernetes config")
            return True
        except Exception as e:
            logger.error(f"Failed to load any Kubernetes config: {e}")
            return False


def validate_directories():
    """Validate and create necessary directories"""
    if not os.path.isdir(config.ORIG):
        logger.warning(
            f"Original root directory '{config.ORIG}' does not exist, creating it..."
        )
        os.makedirs(config.ORIG, exist_ok=True)

    if not os.path.isdir(config.ZIP):
        logger.warning(
            f"Zip root directory '{config.ZIP}' does not exist, creating it..."
        )
        os.makedirs(config.ZIP, exist_ok=True)


def main() -> None:
    """Main function to scan directories and enqueue archive jobs."""
    # Parse arguments
    parser = create_argument_parser()
    args = parser.parse_args()

    # Setup logging
    global logger
    logger = setup_logging(args.log_level)
    logger.info(f"Log level set to: {args.log_level}")

    # Update global configuration
    config.update_from_args(args)

    # Validate directories
    validate_directories()

    execution_env = "batch"
    dry_run: bool = args.dry_run
    export_only: bool = args.export_only

    logger.info(f"Starting scan: ORIG='{config.ORIG}', ZIP='{config.ZIP}'")
    logger.info(
        f"Options: execution_env='{execution_env}', log_level='{args.log_level}', "
        f"dry-run={dry_run}, export_only={export_only}"
    )

    # Setup Kubernetes configuration
    if not setup_kubernetes_config():
        logger.error("Failed to setup Kubernetes configuration")
        sys.exit(1)

    logger.info(f"Scanner initialized. Using backend at {config.BACKEND_URL}")

    # Initialize components
    api_client = APIClient(config.BACKEND_URL)
    scanner = DirectoryScanner(api_client)
    job_manager = JobManager()

    # Collect all changed folders first
    changed_folders = scanner.collect_changed_folders(dry_run)

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
        processed_count = job_manager.queue_batch_zip_job(changed_folders, export_only)
        if processed_count:
            logger.info(f"Successfully created job for {processed_count} folders")
    else:
        logger.info("No changes detected, no batch job needed")

    # Process metacloud files
    metacloud_count = 0
    logger.info("Scanning for .metacloud files...")
    metacloud_changes = scanner.scan_for_metacloud_files(dry_run)
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

        potree_job_count = job_manager.queue_potree_conversion_jobs(
            metacloud_changes, export_only
        )
        if potree_job_count:
            logger.info(
                f"Successfully created potree conversion job for {metacloud_count} files"
            )

    # Update completion message to include metacloud information
    logger.info(
        f"Scan completed: detected {length_changed_folders} folder changes"
        + (f" and {metacloud_count} metacloud changes" if metacloud_count > 0 else "")
    )


if __name__ == "__main__":
    main()
