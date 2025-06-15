"""
Directory scanning logic for detecting changes in LiDAR data folders and metacloud files.
"""

import logging
import os
import time
from typing import List

from .api_client import APIClient
from .config import config
from .file_utils import fingerprint_file, get_directory_stats

logger = logging.getLogger(__name__)


class DirectoryScanner:
    """Scanner for detecting changes in directories and metacloud files"""

    def __init__(self, api_client: APIClient):
        self.api_client = api_client

    def scan_for_metacloud_files(self, dry_run: bool = False) -> List[List[str]]:
        """
        Scan directories for .metacloud files and track changes.

        Args:
            dry_run: Whether to perform a dry run without modifying the database

        Returns:
            List of lists containing [mission_key, metacloud_path, fingerprint] that have changed
        """
        metacloud_changes: List[List[str]] = []

        # First, list all level1 directories (missions)
        for level1 in os.listdir(config.ORIG):
            p1 = os.path.join(config.ORIG, level1)
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

                # Check if we have this mission key in folder_state
                if not self.api_client.check_mission_exists(level1):
                    logger.info(
                        f"Mission {level1} not in folder_state, skipping metacloud processing"
                    )
                    continue

                # Check if the metacloud file has changed or needs reprocessing
                row = self.api_client.get_potree_metacloud_state(level1)

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
                        output_path = os.path.join(
                            os.path.dirname(config.ZIP), "Potree", level1
                        )
                        self.api_client.create_potree_metacloud_state(
                            level1, metacloud_fp, output_path
                        )
                else:
                    # Just update the last_checked timestamp for successful completions
                    if not dry_run:
                        self.api_client.update_potree_metacloud_last_checked(level1)
                    logger.debug(
                        f"No processing needed for .metacloud file in mission {level1} (status: {row.get('processing_status') if row else 'N/A'})"
                    )

            except Exception as e:
                logger.error(f"Error processing metacloud file in {level1}: {e}")

        return metacloud_changes

    def collect_changed_folders(self, dry_run: bool = False) -> List[List[str]]:
        """
        Scan directories and collect paths of changed folders without immediately queueing jobs.

        Args:
            dry_run: Whether to perform a dry run without modifying the database

        Returns:
            List of relative paths to folders that have changed
        """
        changed_folders: List[List[str]] = []

        for level1 in os.listdir(config.ORIG):
            p1 = os.path.join(config.ORIG, level1)
            if not os.path.isdir(p1):
                continue

            for level2 in os.listdir(p1):
                rel = os.path.join(level1, level2)
                src = os.path.join(config.ORIG, rel)
                if not os.path.isdir(src):
                    continue

                try:
                    logger.info(f"Processing directory: {rel}")
                    fp, size, count = get_directory_stats(src)
                    logger.info(
                        f"Fingerprint: {fp}, Size: {size} KB, File Count: {count}"
                    )

                    row = self.api_client.get_folder_state(rel)

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
                            self.api_client.create_folder_state(
                                rel,
                                level1,
                                fp,
                                size,
                                count,
                                os.path.join(config.ZIP, f"{rel}.tar.gz"),
                            )
                    else:
                        logger.debug(
                            f"No processing needed for {rel} (status: {row.get('processing_status') if row else 'N/A'})"
                        )

                except Exception as e:
                    logger.error(f"Error processing directory {rel}: {e}")

        return changed_folders
