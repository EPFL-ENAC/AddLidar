from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import time
import sqlite3

from .base import get_db_connection, QueryResult, logger
from src.api.mission_protection_utils import is_mission_protected, validate_mission_password


# Pydantic models specific to potree metacloud
class PotreeMetacloudStateResponse(BaseModel):
    mission_key: str
    fp: Optional[str]
    output_path: Optional[str]
    last_checked: int
    last_processed: Optional[int]
    processing_time: Optional[int]
    processing_status: Optional[str]
    error_message: Optional[str]
    detailed_error_message: Optional[str]
    metacloud_filename: Optional[str]
    name: Optional[str]
    date: Optional[str]
    extra_attributes: Optional[str]  # JSON string


class PotreeMetacloudStateUpdate(BaseModel):
    fingerprint: Optional[str] = None
    processing_status: Optional[str]  # 'success', 'failed', 'empty'
    processing_time: Optional[int] = None
    error_message: Optional[str] = None
    detailed_error_message: Optional[str] = None
    metacloud_filename: Optional[str] = None
    name: Optional[str] = None
    date: Optional[str] = None
    extra_attributes: Optional[str] = None  # JSON string


class PotreeMetacloudStateCreate(BaseModel):
    mission_key: str
    fingerprint: str
    output_path: str
    processing_status: Optional[str] = "pending"
    metacloud_filename: Optional[str] = None
    name: Optional[str] = None
    date: Optional[str] = None
    extra_attributes: Optional[str] = None  # JSON string


# Create routers
public_router = APIRouter()
internal_router = APIRouter()


def filter_protected_missions(rows: List, password: Optional[str] = None) -> List[Dict]:
    """Filter out protected missions unless valid password is provided."""
    data = []
    for row in rows:
        row_dict = dict(row)
        mission_key = row_dict.get("mission_key")

        if mission_key and is_mission_protected(mission_key):
            if password and validate_mission_password(mission_key, password):
                data.append(row_dict)
        else:
            data.append(row_dict)
    return data


@public_router.get("/potree_metacloud_state", response_model=QueryResult)
async def get_potree_metacloud_state_public(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    x_mission_password: Optional[str] = Header(None, description="Password for protected missions"),
):
    """Get potree metacloud state (Public API - enforces password protection)"""
    result = await get_potree_metacloud_state_internal(limit, offset)
    result.data = filter_protected_missions(
        [sqlite3.Row(keys=d.keys(), values=d.values()) for d in result.data], x_mission_password
    )
    result.count = len(result.data)
    return result


@internal_router.get("/potree_metacloud_state", response_model=QueryResult)
async def get_potree_metacloud_state_internal(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get potree metacloud state (Internal API - no password protection)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query potree_metacloud_state table
    query = """
    SELECT
      mission_key,
      fp,
      output_path,
      last_checked,
      last_processed,
      processing_time,
      processing_status,
      error_message,
      detailed_error_message,
      metacloud_filename,
      name,
      date,
      extra_attributes,
      datetime(last_checked,'unixepoch') AS last_checked_time,
      datetime(last_processed,'unixepoch') AS last_processed_time
    FROM potree_metacloud_state
    ORDER BY last_checked DESC
    LIMIT ? OFFSET ?
    """

    # Execute query
    cursor.execute(query, (limit, offset))
    rows = cursor.fetchall()

    # Get total count
    cursor.execute("SELECT COUNT(*) as count FROM potree_metacloud_state")
    count = cursor.fetchone()["count"]

    conn.close()

    # Convert rows to list of dicts
    data = [dict(row) for row in rows]

    return QueryResult(data=data, count=count)


@internal_router.put("/potree_metacloud_state/{mission_key:path}", response_model=Dict[str, Any])
async def update_potree_metacloud_state(mission_key: str, update_data: PotreeMetacloudStateUpdate):
    """Update potree metacloud state record (Internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if record exists
    cursor.execute(
        "SELECT mission_key FROM potree_metacloud_state WHERE mission_key = ?",
        (mission_key,),
    )
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Potree metacloud state record not found for mission_key: {mission_key}",
        )

    # Build update query dynamically based on provided fields
    update_fields = ["last_processed = ?"]
    update_values = [int(time.time())]  # Current timestamp

    update_fields.append("processing_status = ?")
    update_values.append(update_data.processing_status)

    if update_data.fingerprint is not None:
        update_fields.append("fp = ?")
        update_values.append(update_data.fingerprint)

    if update_data.processing_time is not None:
        update_fields.append("processing_time = ?")
        update_values.append(update_data.processing_time)

    if update_data.error_message is not None:
        update_fields.append("error_message = ?")
        update_values.append(update_data.error_message)
    else:
        # Clear error message on success
        if update_data.processing_status == "success":
            update_fields.append("error_message = NULL")

    if update_data.detailed_error_message is not None:
        update_fields.append("detailed_error_message = ?")
        update_values.append(update_data.detailed_error_message)
    else:
        # Clear detailed error message on success
        if update_data.processing_status == "success":
            update_fields.append("detailed_error_message = NULL")

    # Add metacloud_filename if provided
    if hasattr(update_data, "metacloud_filename") and update_data.metacloud_filename is not None:
        update_fields.append("metacloud_filename = ?")
        update_values.append(update_data.metacloud_filename)

    # Add name if provided
    if update_data.name is not None:
        update_fields.append("name = ?")
        update_values.append(update_data.name)

    # Add date if provided
    if update_data.date is not None:
        update_fields.append("date = ?")
        update_values.append(update_data.date)

    # Add extra_attributes if provided
    if update_data.extra_attributes is not None:
        update_fields.append("extra_attributes = ?")
        update_values.append(update_data.extra_attributes)

    # Add mission_key for WHERE clause
    update_values.append(mission_key)

    update_query = f"""
    UPDATE potree_metacloud_state 
    SET {', '.join(update_fields)}
    WHERE mission_key = ?
    """

    cursor.execute(update_query, update_values)
    conn.commit()

    # Return updated record
    cursor.execute(
        """SELECT mission_key, fp, processing_status, 
           processing_time, error_message, detailed_error_message, last_processed 
           FROM potree_metacloud_state WHERE mission_key = ?""",
        (mission_key,),
    )
    updated_record = cursor.fetchone()
    conn.close()

    return {
        "message": "Potree metacloud state updated successfully",
        "record": dict(updated_record),
    }


@public_router.get("/potree_metacloud_state/{mission_key}", response_model=Dict[str, Any])
async def get_potree_metacloud_state_by_mission_public(
    mission_key: str,
    x_mission_password: Optional[str] = Header(None, description="Password for protected missions"),
):
    """Get potree metacloud state for mission (Public API - enforces password protection)"""
    # Check if mission is protected and validate password
    if is_mission_protected(mission_key):
        if not x_mission_password:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Mission is password protected",
                    "mission_key": mission_key,
                    "protected": True,
                },
            )
        if not validate_mission_password(mission_key, x_mission_password):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Invalid password for protected mission",
                    "mission_key": mission_key,
                    "protected": True,
                },
            )

    return await get_potree_metacloud_state_by_mission_internal(mission_key)


@internal_router.get("/potree_metacloud_state/{mission_key}", response_model=Dict[str, Any])
async def get_potree_metacloud_state_by_mission_internal(mission_key: str):
    """Get potree metacloud state for mission (Internal API - no password protection)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for specific mission
    query = """
    SELECT
      mission_key,
      fp,
      output_path,
      last_checked,
      last_processed,
      processing_time,
      processing_status,
      error_message,
      detailed_error_message,
      metacloud_filename,
      name,
      date,
      extra_attributes,
      datetime(last_checked,'unixepoch') AS last_checked_time,
      datetime(last_processed,'unixepoch') AS last_processed_time
    FROM potree_metacloud_state
    WHERE mission_key = ?
    """

    cursor.execute(query, (mission_key,))
    row = cursor.fetchone()

    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Potree metacloud state not found for mission: {mission_key}",
        )

    return dict(row)


@internal_router.post("/potree_metacloud_state", response_model=Dict[str, Any])
async def create_potree_metacloud_state(create_data: PotreeMetacloudStateCreate):
    """Create new potree metacloud state record (Internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    current_time = int(time.time())

    try:
        cursor.execute(
            """INSERT INTO potree_metacloud_state
            (mission_key, fp, output_path, last_checked, last_processed, processing_status, metacloud_filename, name, date, extra_attributes)
            VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?, ?)
            ON CONFLICT(mission_key) DO UPDATE SET
            fp = excluded.fp,
            output_path = excluded.output_path,
            last_checked = excluded.last_checked,
            last_processed = NULL,
            processing_status = excluded.processing_status,
            metacloud_filename = excluded.metacloud_filename,
            name = excluded.name,
            date = excluded.date,
            extra_attributes = excluded.extra_attributes""",
            (
                create_data.mission_key,
                create_data.fingerprint,
                create_data.output_path,
                current_time,
                create_data.processing_status,
                create_data.metacloud_filename,
                create_data.name,
                create_data.date,
                create_data.extra_attributes,
            ),
        )
        conn.commit()

        # Return created record
        cursor.execute(
            """SELECT mission_key, fp, output_path, processing_status, 
               last_checked, name, date, extra_attributes FROM potree_metacloud_state WHERE mission_key = ?""",
            (create_data.mission_key,),
        )
        created_record = cursor.fetchone()
        conn.close()

        return {
            "message": "Potree metacloud state created successfully",
            "record": dict(created_record),
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error creating potree metacloud state: {str(e)}")


@internal_router.patch(
    "/potree_metacloud_state/{mission_key:path}/last_checked",
    response_model=Dict[str, Any],
)
async def update_potree_metacloud_last_checked(mission_key: str):
    """Update only the last_checked timestamp for potree metacloud state (Internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if record exists
    cursor.execute(
        "SELECT mission_key FROM potree_metacloud_state WHERE mission_key = ?",
        (mission_key,),
    )
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Potree metacloud state record not found for mission_key: {mission_key}",
        )

    # Update only last_checked timestamp
    current_time = int(time.time())
    cursor.execute(
        "UPDATE potree_metacloud_state SET last_checked = ? WHERE mission_key = ?",
        (current_time, mission_key),
    )
    conn.commit()

    # Return updated record
    cursor.execute(
        """SELECT mission_key, fp, processing_status, 
           processing_time, error_message, detailed_error_message, last_checked 
           FROM potree_metacloud_state WHERE mission_key = ?""",
        (mission_key,),
    )
    updated_record = cursor.fetchone()
    conn.close()

    return {
        "message": "Potree metacloud state last_checked updated successfully",
        "record": dict(updated_record),
    }
