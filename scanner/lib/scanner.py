"""Directory scanning and change detection logic."""

import os
import json
import logging
from typing import List
import shutil

from .api_client import APIClient
from .filesystem import get_directory_stats, fingerprint_file
from .metacloud_parser import parse_metacloud_file

logger = logging.getLogger(__name__)


class DirectoryScanner:
    def __init__(self, api_client: APIClient, original_root: str, zip_root: str):
        self.api_client = api_client
        self.original_root = original_root
        self.zip_root = zip_root

    def copy_footprint_files(self) -> None:
        """Copy footprint.geojson files to zip_root/Footprints/ directory."""
        footprints_dir = os.path.join(self.zip_root, "Footprints")

        # Create Footprints directory if it doesn't exist
        os.makedirs(footprints_dir, exist_ok=True)
        logger.info(f"Footprints directory: {footprints_dir}")

        if not os.path.exists(self.original_root):
            logger.warning(
                f"Original root directory {self.original_root} does not exist"
            )
            return

        copied_count = 0
        skipped_count = 0

        try:
            # Iterate through all directories in original_root (level1 directories)
            for level1 in os.listdir(self.original_root):
                project_path = os.path.join(self.original_root, level1)

                # Skip if not a directory
                if not os.path.isdir(project_path):
                    continue

                # Look for footprint.geojson in the project directory
                footprint_source = os.path.join(project_path, "footprint.geojson")

                if os.path.exists(footprint_source):
                    # Destination file named after the project directory
                    footprint_dest = os.path.join(footprints_dir, f"{level1}.geojson")

                    try:
                        # Copy the footprint file
                        shutil.copy2(footprint_source, footprint_dest)
                        logger.debug(
                            f"Copied footprint: {footprint_source} -> {footprint_dest}"
                        )
                        copied_count += 1

                    except Exception as e:
                        logger.error(f"Failed to copy footprint for {level1}: {e}")

                else:
                    logger.debug(f"No footprint.geojson found in {project_path}")
                    skipped_count += 1

        except Exception as e:
            logger.error(f"Error scanning for footprint files: {e}")
            return

        logger.info(
            f"Footprint copying completed: {copied_count} copied, {skipped_count} skipped"
        )

    def scan_for_password_files(self, dry_run: bool = False) -> None:
        """Scan missions for .password files and update protection status."""
        for level1 in os.listdir(self.original_root):
            p1 = os.path.join(self.original_root, level1)
            if not os.path.isdir(p1):
                continue

            # Look for .password file in the mission directory
            password_file = os.path.join(p1, ".password")

            if os.path.exists(password_file):
                try:
                    # Read the password from the file
                    with open(password_file, "r") as f:
                        password = f.read().strip()

                    if not password:
                        logger.warning(
                            f"Empty .password file found in mission {level1}"
                        )
                        continue

                    # Hash the password content to check for changes
                    password_fp = fingerprint_file(password_file)
                    logger.info(
                        f"Found .password file in mission {level1}, fingerprint: {password_fp}"
                    )

                    # Check current protection status
                    protection = self.api_client.get_mission_protection(level1)

                    if not protection or not protection.get("is_protected"):
                        logger.info(
                            f"Creating password protection for mission {level1}"
                        )
                        if not dry_run:
                            self.api_client.create_mission_protection(level1, password)
                    else:
                        # Update last_checked timestamp
                        if not dry_run:
                            self.api_client.update_mission_protection_last_checked(
                                level1
                            )

                except Exception as e:
                    logger.error(
                        f"Error processing .password file in mission {level1}: {e}"
                    )
            else:
                # No .password file found - check if protection exists and should be removed
                protection = self.api_client.get_mission_protection(level1)
                if protection and protection.get("is_protected"):
                    logger.info(
                        f"No .password file found but mission {level1} is protected - removing protection"
                    )
                    if not dry_run:
                        self.api_client.delete_mission_protection(level1)

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

                # Extract just the filename from the full path
                metacloud_filename = os.path.basename(metacloud_file)

                if needs_processing:
                    metacloud_changes.append([level1, metacloud_file, metacloud_fp])
                    if not dry_run:
                        output_path = os.path.join(
                            os.path.dirname(self.zip_root), "Potree", level1
                        )
                        # Parse metacloud file for attributes
                        parsed_attrs = parse_metacloud_file(metacloud_file)
                        if parsed_attrs.has_errors:
                            for error in parsed_attrs.errors:
                                logger.warning(
                                    f"Metacloud parse issue in {level1}: {error}"
                                )

                        # Serialize extra_attributes to JSON if present
                        extra_attrs_json = None
                        if parsed_attrs.extra_attributes:
                            extra_attrs_json = json.dumps(parsed_attrs.extra_attributes)

                        logger.info(
                            f"Parsed metacloud attributes for {level1}: "
                            f"name={parsed_attrs.name}, date={parsed_attrs.date}, "
                            f"extra_attrs={len(parsed_attrs.extra_attributes)} keys"
                        )

                        self.api_client.create_potree_metacloud_state(
                            level1,
                            metacloud_fp,
                            output_path,
                            metacloud_filename=metacloud_filename,
                            name=parsed_attrs.name,
                            date=parsed_attrs.date,
                            extra_attributes=extra_attrs_json,
                        )
                else:
                    if not dry_run:
                        self.api_client.update_potree_metacloud_last_checked(
                            level1, metacloud_filename=metacloud_filename
                        )

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

                    # Check if folder is empty (no files)
                    if count == 0:
                        logger.info(
                            f"Empty folder detected: {rel} - marking as 'empty' status"
                        )
                        if not dry_run:
                            self.api_client.create_folder_state_empty(
                                rel,
                                level1,
                                fp,
                                size,
                                count,
                                os.path.join(self.zip_root, f"{rel}.tar.gz"),
                            )
                        continue

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
