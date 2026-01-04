"""Mission protection utilities and middleware."""

import sqlite3
import bcrypt
import logging
from typing import Optional
from fastapi import HTTPException, Header

from src.config.settings import settings

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get database connection"""
    try:
        import os

        db_path = os.getenv("DATABASE_PATH", settings.DATABASE_PATH)
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise


def is_mission_protected(mission_key: str) -> bool:
    """Check if a mission is password protected"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT mission_key FROM mission_protection WHERE mission_key = ?",
            (mission_key,),
        )
        result = cursor.fetchone()
        conn.close()
        return result is not None
    except Exception as e:
        logger.error(f"Error checking mission protection for {mission_key}: {e}")
        return False


def validate_mission_password(mission_key: str, password: str) -> bool:
    """Validate a password for a protected mission"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT password_hash FROM mission_protection WHERE mission_key = ?",
            (mission_key,),
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return False

        password_hash = row["password_hash"]
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception as e:
        logger.error(f"Error validating password for mission {mission_key}: {e}")
        return False


def check_mission_access(mission_key: str, password: Optional[str] = None) -> None:
    """Check if access to a mission is allowed, raise HTTPException if not"""
    if not mission_key:
        return

    if is_mission_protected(mission_key):
        if not password:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Mission is password protected",
                    "mission_key": mission_key,
                    "protected": True,
                },
            )

        if not validate_mission_password(mission_key, password):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Invalid password for protected mission",
                    "mission_key": mission_key,
                    "protected": True,
                },
            )


def extract_mission_from_path(file_path: str) -> Optional[str]:
    """Extract mission key from a file path.
    Assumes path format: /data/MISSION_KEY/... or /LiDAR/MISSION_KEY/...
    """
    try:
        parts = file_path.strip("/").split("/")
        if len(parts) >= 2:
            # If path starts with 'data' or 'LiDAR', the mission is the next part
            if parts[0] in ["data", "LiDAR"]:
                return parts[1]
            # Otherwise, assume first part is the mission
            return parts[0]
        return None
    except Exception as e:
        logger.error(f"Error extracting mission from path {file_path}: {e}")
        return None
