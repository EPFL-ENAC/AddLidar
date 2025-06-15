"""
Utilities for file system operations, fingerprinting, and directory scanning.
"""

import hashlib
import logging
import os
import subprocess
from typing import Tuple

logger = logging.getLogger(__name__)


def fingerprint_file(file_path: str) -> str:
    """
    Generate a unique fingerprint for a single file.

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 hash representing the file content
    """
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


def fingerprint_directory(path: str) -> str:
    """
    Generate a unique fingerprint for a directory based on file attributes.

    Args:
        path: Directory path to fingerprint

    Returns:
        SHA-256 hash representing the directory content state
    """
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
    fp = fingerprint_directory(path)
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
