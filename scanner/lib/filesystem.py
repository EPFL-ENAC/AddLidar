"""Filesystem utilities and fingerprinting functions."""

import os
import subprocess
import logging
import hashlib
from typing import Tuple

logger = logging.getLogger(__name__)


def fingerprint_file(file_path: str) -> str:
    """Generate a unique fingerprint for a single file."""
    try:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate fingerprint for file {file_path}: {e}")
        raise


def fingerprint_directory(path: str) -> str:
    """Generate a unique fingerprint for a directory based on file attributes."""
    try:
        file_info = []

        for root, _, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)

                stat_result = os.stat(full_path, follow_symlinks=False)
                size_bytes = stat_result.st_size

                file_info.append((rel_path, size_bytes))

        file_info.sort()
        hasher = hashlib.sha256()

        for rel_path, size_bytes in file_info:
            file_data = f"{rel_path}|{size_bytes}\n".encode("utf-8")
            hasher.update(file_data)

        return hasher.hexdigest()
    except Exception as e:
        logger.error(f"Failed to generate fingerprint for {path}: {e}")
        raise


def get_directory_stats(path: str) -> Tuple[str, int, int]:
    """Get directory statistics: fingerprint, size in KB, and file count."""
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
