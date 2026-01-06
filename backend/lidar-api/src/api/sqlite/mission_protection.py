import time
import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from .base import get_db_connection, logger

# Create routers
public_router = APIRouter()
internal_router = APIRouter()


class MissionProtectionStatus(BaseModel):
    mission_key: str
    is_protected: bool
    last_checked: Optional[int] = None
    created_at: Optional[int] = None
    updated_at: Optional[int] = None


class MissionProtectionCreate(BaseModel):
    mission_key: str
    password: str


class MissionProtectionUpdate(BaseModel):
    password_hash: str


class PasswordValidation(BaseModel):
    password: str


@public_router.get("/mission_protection/{mission_key:path}", response_model=MissionProtectionStatus)
@internal_router.get("/mission_protection/{mission_key:path}", response_model=MissionProtectionStatus)
async def get_mission_protection_status(mission_key: str):
    """Check if a mission is password protected"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT mission_key, password_hash, last_checked, created_at, updated_at
        FROM mission_protection
        WHERE mission_key = ?
        """,
        (mission_key,),
    )
    row = cursor.fetchone()
    conn.close()

    if row:
        return MissionProtectionStatus(
            mission_key=row["mission_key"],
            is_protected=True,
            last_checked=row["last_checked"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
    else:
        return MissionProtectionStatus(
            mission_key=mission_key,
            is_protected=False,
        )


@public_router.post("/mission_protection/{mission_key:path}/validate")
async def validate_mission_password(mission_key: str, payload: PasswordValidation) -> Dict[str, Any]:
    """Validate a password for a protected mission"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT password_hash
        FROM mission_protection
        WHERE mission_key = ?
        """,
        (mission_key,),
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Mission not found or not protected")

    password_hash = row["password_hash"]
    is_valid = bcrypt.checkpw(payload.password.encode("utf-8"), password_hash.encode("utf-8"))

    return {
        "mission_key": mission_key,
        "valid": is_valid,
    }


@internal_router.post("/mission_protection", response_model=MissionProtectionStatus)
async def create_mission_protection(payload: MissionProtectionCreate):
    """Create password protection for a mission (internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if already exists
    cursor.execute(
        "SELECT mission_key FROM mission_protection WHERE mission_key = ?",
        (payload.mission_key,),
    )
    existing = cursor.fetchone()

    now = int(time.time())

    # Hash the password using bcrypt
    password_hash = bcrypt.hashpw(payload.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    if existing:
        # Update existing
        cursor.execute(
            """
            UPDATE mission_protection
            SET password_hash = ?, updated_at = ?, last_checked = ?
            WHERE mission_key = ?
            """,
            (password_hash, now, now, payload.mission_key),
        )
        conn.commit()
        conn.close()
        logger.info(f"Updated password protection for mission {payload.mission_key}")
    else:
        # Insert new
        cursor.execute(
            """
            INSERT INTO mission_protection (mission_key, password_hash, last_checked, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (payload.mission_key, password_hash, now, now, now),
        )
        conn.commit()
        conn.close()
        logger.info(f"Created password protection for mission {payload.mission_key}")

    return MissionProtectionStatus(
        mission_key=payload.mission_key,
        is_protected=True,
        last_checked=now,
        created_at=now,
        updated_at=now,
    )


@internal_router.put("/mission_protection/{mission_key:path}", response_model=MissionProtectionStatus)
async def update_mission_protection(mission_key: str, payload: MissionProtectionUpdate):
    """Update password hash for a mission (internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exists
    cursor.execute(
        "SELECT mission_key FROM mission_protection WHERE mission_key = ?",
        (mission_key,),
    )
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Mission protection not found")

    now = int(time.time())

    cursor.execute(
        """
        UPDATE mission_protection
        SET password_hash = ?, updated_at = ?, last_checked = ?
        WHERE mission_key = ?
        """,
        (payload.password_hash, now, now, mission_key),
    )
    conn.commit()
    conn.close()

    logger.info(f"Updated password protection for mission {mission_key}")

    return MissionProtectionStatus(
        mission_key=mission_key,
        is_protected=True,
        last_checked=now,
        updated_at=now,
    )


@internal_router.patch("/mission_protection/{mission_key:path}/last_checked")
async def update_mission_protection_last_checked(mission_key: str) -> Dict[str, Any]:
    """Update the last_checked timestamp for a mission"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if exists
    cursor.execute(
        "SELECT mission_key FROM mission_protection WHERE mission_key = ?",
        (mission_key,),
    )
    existing = cursor.fetchone()

    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Mission protection not found")

    now = int(time.time())

    cursor.execute(
        """
        UPDATE mission_protection
        SET last_checked = ?
        WHERE mission_key = ?
        """,
        (now, mission_key),
    )
    conn.commit()
    conn.close()

    return {"mission_key": mission_key, "last_checked": now}


@internal_router.delete("/mission_protection/{mission_key:path}")
async def delete_mission_protection(mission_key: str) -> Dict[str, Any]:
    """Remove password protection from a mission"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM mission_protection WHERE mission_key = ?",
        (mission_key,),
    )
    rows_deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if rows_deleted == 0:
        raise HTTPException(status_code=404, detail="Mission protection not found")

    logger.info(f"Deleted password protection for mission {mission_key}")

    return {"mission_key": mission_key, "deleted": True}
