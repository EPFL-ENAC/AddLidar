"""Directory scanning and change detection logic."""

import os
import time
import logging
from typing import List

from .api_client import APIClient
from .filesystem import get_directory_stats, fingerprint_file

logger = logging.getLogger(__name__)

logger = logging.getLogger(__name__)


class DirectoryScanner:
    def __init__(self, api_client: APIClient, original_root: str, zip_root: str):
        self.api_client = api_client
        self.original_root = original_root
        self.zip_root = zip_root

    def scan_for_metacloud_files(self, dry_run: bool = False) -> List[List[str]]:
        """Scan directories for .metacloud files and track changes."""
        metacloud_changes: List[List[str]] = []

        for level1 in os.listdir(self.original_root):
            p1 = os.path.join(self.original_root, level1)
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

            try:
                metacloud_fp = fingerprint_file(metacloud_file)
                logger.info(
                    f"Found .metacloud file in {level1}, fingerprint: {metacloud_fp}"
                )

                row = self.api_client.get_potree_metacloud_state(level1)

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
                        f"Incomplete processing detected for .metacloud file in mission {level1}"
                    )
                    needs_processing = True

                if needs_processing:
                    metacloud_changes.append([level1, metacloud_file, metacloud_fp])
                    if not dry_run:
                        output_path = os.path.join(
                            os.path.dirname(self.zip_root), "Potree", level1
                        )
                        self.api_client.create_potree_metacloud_state(
                            level1, metacloud_fp, output_path
                        )
                else:
                    if not dry_run:
                        self.api_client.update_potree_metacloud_last_checked(level1)

            except Exception as e:
                logger.error(f"Error processing metacloud file in {level1}: {e}")

        return metacloud_changes

    def collect_changed_folders(self, dry_run: bool = False) -> List[List[str]]:
        """Scan directories and collect paths of changed folders."""
        changed_folders: List[List[str]] = []

        for level1 in os.listdir(self.original_root):
            p1 = os.path.join(self.original_root, level1)
            if not os.path.isdir(p1):
                continue

            for level2 in os.listdir(p1):
                rel = os.path.join(level1, level2)
                src = os.path.join(self.original_root, rel)
                if not os.path.isdir(src):
                    continue

                try:
                    logger.info(f"Processing directory: {rel}")
                    fp, size, count = get_directory_stats(src)
                    logger.info(
                        f"Fingerprint: {fp}, Size: {size} KB, File Count: {count}"
                    )

                    row = self.api_client.get_folder_state(rel)

                    needs_processing = False
                    if not row:
                        logger.info(f"New folder detected: {rel}")
                        needs_processing = True
                    elif row.get("fp") != fp:
                        logger.info(f"Fingerprint change detected in {rel}")
                        needs_processing = True
                    elif row.get("processing_status") in ("pending", "failed", None):
                        logger.info(f"Incomplete processing detected in {rel}")
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
                                os.path.join(self.zip_root, f"{rel}.tar.gz"),
                            )
                    else:
                        if not dry_run:
                            self.api_client.update_folder_last_checked(rel)

                except Exception as e:
                    logger.error(f"Error processing directory {rel}: {e}")

        return changed_folders
