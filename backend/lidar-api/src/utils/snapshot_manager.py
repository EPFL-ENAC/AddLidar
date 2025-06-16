#!/usr/bin/env python3
"""
Production Database Snapshot Manager

This utility helps manage database snapshots from production environments.
It can:
1. Download database snapshots from Kubernetes production pods
2. List available snapshots locally
3. Switch between different database snapshots for development
4. Create local backups before switching
"""

import os
import sys
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SnapshotManager:
    def __init__(self, base_dir: str = None):
        """Initialize the snapshot manager

        Args:
            base_dir: Base directory for the lidar-api project.
                     If None, tries to detect from current script location.
        """
        if base_dir is None:
            # Try to detect base directory from script location
            current_file = Path(__file__).resolve()
            # Navigate up from src/utils/ to the lidar-api root
            self.base_dir = current_file.parent.parent.parent
        else:
            self.base_dir = Path(base_dir)

        self.data_dir = self.base_dir / "data"
        self.snapshots_dir = self.base_dir / "snapshots"
        self.current_db_path = self.data_dir / "database.db"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.snapshots_dir.mkdir(exist_ok=True)

        logger.info(f"Snapshot manager initialized for: {self.base_dir}")
        logger.info(f"Snapshots directory: {self.snapshots_dir}")
        logger.info(f"Current database: {self.current_db_path}")

    def get_production_pods(
        self, namespace: str = "epfl-eso-addlidar-prod"
    ) -> List[str]:
        """Get list of production pods that might contain the database

        Args:
            namespace: Kubernetes namespace for production

        Returns:
            List of pod names
        """
        try:
            cmd = ["kubectl", "get", "pods", "-n", namespace, "-o", "name"]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            pods = []
            for line in result.stdout.strip().split("\n"):
                if line.startswith("pod/"):
                    pod_name = line.replace("pod/", "")
                    # Filter for relevant pods (backend, api, etc.)
                    if any(
                        keyword in pod_name.lower()
                        for keyword in ["backend", "api", "lidar"]
                    ):
                        pods.append(pod_name)

            return pods
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to get production pods: {e}")
            return []
        except FileNotFoundError:
            logger.error(
                "kubectl not found. Please install kubectl and configure access to the cluster."
            )
            return []

    def download_snapshot_from_pod(
        self,
        pod_name: str,
        namespace: str = "epfl-eso-addlidar-prod",
        remote_db_path: str = "/db-path/lidar-archive.db",
    ) -> Optional[str]:
        """Download database snapshot from a production pod

        Args:
            pod_name: Name of the Kubernetes pod
            namespace: Kubernetes namespace
            remote_db_path: Path to database file in the pod

        Returns:
            Local path to downloaded snapshot or None if failed
        """
        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        local_snapshot_path = self.snapshots_dir / f"snapshot_prod_{timestamp}.db"

        try:
            # Use kubectl cp to copy the database file
            cmd = [
                "kubectl",
                "cp",
                f"{namespace}/{pod_name}:{remote_db_path}",
                str(local_snapshot_path),
            ]

            logger.info(f"Downloading snapshot from {pod_name}...")
            logger.info(f"Command: {' '.join(cmd)}")

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            if local_snapshot_path.exists():
                file_size = local_snapshot_path.stat().st_size
                logger.info(f"Successfully downloaded snapshot: {local_snapshot_path}")
                logger.info(f"File size: {file_size:,} bytes")
                return str(local_snapshot_path)
            else:
                logger.error("Snapshot file was not created")
                return None

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download snapshot from {pod_name}: {e}")
            if e.stderr:
                logger.error(f"Error output: {e.stderr}")
            return None

    def list_local_snapshots(self) -> List[Tuple[str, datetime, int]]:
        """List all local database snapshots

        Returns:
            List of tuples (filename, modification_time, file_size)
        """
        snapshots = []

        # Check both snapshots directory and root directory for existing snapshots
        search_locations = [self.snapshots_dir, self.base_dir]

        for location in search_locations:
            if location.exists():
                for file_path in location.glob("*.db"):
                    if "snapshot" in file_path.name or file_path.name.startswith(
                        "snapshot_"
                    ):
                        stat = file_path.stat()
                        mod_time = datetime.fromtimestamp(stat.st_mtime)
                        snapshots.append((str(file_path), mod_time, stat.st_size))

        # Sort by modification time (newest first)
        snapshots.sort(key=lambda x: x[1], reverse=True)
        return snapshots

    def backup_current_database(self) -> Optional[str]:
        """Create a backup of the current database before switching

        Returns:
            Path to backup file or None if failed
        """
        if not self.current_db_path.exists():
            logger.warning("No current database to backup")
            return None

        timestamp = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        backup_path = self.snapshots_dir / f"backup_local_{timestamp}.db"

        try:
            shutil.copy2(self.current_db_path, backup_path)
            logger.info(f"Current database backed up to: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"Failed to backup current database: {e}")
            return None

    def switch_to_snapshot(
        self, snapshot_path: str, create_backup: bool = True
    ) -> bool:
        """Switch the current database to use a specific snapshot

        Args:
            snapshot_path: Path to the snapshot to switch to
            create_backup: Whether to backup current database first

        Returns:
            True if successful, False otherwise
        """
        snapshot_file = Path(snapshot_path)

        if not snapshot_file.exists():
            logger.error(f"Snapshot file not found: {snapshot_path}")
            return False

        # Backup current database if requested and it exists
        if create_backup and self.current_db_path.exists():
            backup_path = self.backup_current_database()
            if backup_path:
                logger.info(f"Current database backed up to: {backup_path}")

        try:
            # Copy snapshot to current database location
            shutil.copy2(snapshot_file, self.current_db_path)
            logger.info(f"Successfully switched to snapshot: {snapshot_path}")
            logger.info(f"Current database is now: {self.current_db_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to switch to snapshot: {e}")
            return False

    def auto_download_latest(
        self, namespace: str = "epfl-eso-addlidar-prod"
    ) -> Optional[str]:
        """Automatically download the latest snapshot from production

        Args:
            namespace: Kubernetes namespace for production

        Returns:
            Path to downloaded snapshot or None if failed
        """
        logger.info("Looking for production pods...")
        pods = self.get_production_pods(namespace)

        if not pods:
            logger.error("No suitable production pods found")
            return None

        logger.info(f"Found {len(pods)} potential pods: {pods}")

        # Try each pod until we find one with a database
        for pod in pods:
            logger.info(f"Attempting to download from pod: {pod}")
            snapshot_path = self.download_snapshot_from_pod(pod, namespace)
            if snapshot_path:
                return snapshot_path

        logger.error("Failed to download snapshot from any pod")
        return None


def main():
    """Command line interface for the snapshot manager"""
    parser = argparse.ArgumentParser(description="Manage production database snapshots")
    parser.add_argument("--base-dir", help="Base directory for lidar-api project")
    parser.add_argument(
        "--namespace",
        default="epfl-eso-addlidar-prod",
        help="Kubernetes namespace (default: epfl-eso-addlidar-prod)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List command
    list_parser = subparsers.add_parser("list", help="List local snapshots")

    # Download command
    download_parser = subparsers.add_parser(
        "download", help="Download snapshot from production"
    )
    download_parser.add_argument("--pod", help="Specific pod name to download from")
    download_parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically find and download from production",
    )

    # Switch command
    switch_parser = subparsers.add_parser(
        "switch", help="Switch to a specific snapshot"
    )
    switch_parser.add_argument("snapshot_path", help="Path to snapshot file")
    switch_parser.add_argument(
        "--no-backup", action="store_true", help="Don't backup current database"
    )

    # Backup command
    backup_parser = subparsers.add_parser("backup", help="Backup current database")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize snapshot manager
    manager = SnapshotManager(args.base_dir)

    if args.command == "list":
        snapshots = manager.list_local_snapshots()
        if snapshots:
            print("\nLocal database snapshots:")
            print("-" * 80)
            print(f"{'Filename':<50} {'Modified':<20} {'Size':<15}")
            print("-" * 80)
            for path, mod_time, size in snapshots:
                filename = Path(path).name
                size_mb = size / (1024 * 1024)
                print(
                    f"{filename:<50} {mod_time.strftime('%Y-%m-%d %H:%M:%S'):<20} {size_mb:.1f} MB"
                )
        else:
            print("No local snapshots found")

    elif args.command == "download":
        if args.auto:
            snapshot_path = manager.auto_download_latest(args.namespace)
            if snapshot_path:
                print(f"Successfully downloaded snapshot: {snapshot_path}")
            else:
                print("Failed to download snapshot")
                sys.exit(1)
        elif args.pod:
            snapshot_path = manager.download_snapshot_from_pod(args.pod, args.namespace)
            if snapshot_path:
                print(f"Successfully downloaded snapshot: {snapshot_path}")
            else:
                print("Failed to download snapshot")
                sys.exit(1)
        else:
            print("Please specify --auto or --pod <pod_name>")
            sys.exit(1)

    elif args.command == "switch":
        success = manager.switch_to_snapshot(args.snapshot_path, not args.no_backup)
        if success:
            print(f"Successfully switched to snapshot: {args.snapshot_path}")
        else:
            print("Failed to switch snapshot")
            sys.exit(1)

    elif args.command == "backup":
        backup_path = manager.backup_current_database()
        if backup_path:
            print(f"Current database backed up to: {backup_path}")
        else:
            print("Failed to backup database")
            sys.exit(1)


if __name__ == "__main__":
    main()
