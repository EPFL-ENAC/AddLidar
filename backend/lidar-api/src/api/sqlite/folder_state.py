from fastapi import APIRouter, HTTPException, Query, Header
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import time
import sqlite3

from .base import get_db_connection, QueryResult, logger
from src.api.mission_protection_utils import is_mission_protected, validate_mission_password


# Pydantic models specific to folder state
class FolderStateResponse(BaseModel):
    folder_key: str
    mission_key: str
    fp: str
    output_path: str
    size_kb: int
    file_count: int
    last_checked: int
    last_processed: Optional[int]
    processing_time: Optional[int]
    processing_status: Optional[str]
    error_message: Optional[str]
    detailed_error_message: Optional[str]


class FolderStateUpdate(BaseModel):
    fingerprint: Optional[str] = None
    processing_status: Optional[str]  # 'success', 'failed', 'empty'
    processing_time: Optional[int] = None
    error_message: Optional[str] = None
    detailed_error_message: Optional[str] = None


class FolderStateCreate(BaseModel):
    folder_key: str
    mission_key: str
    fingerprint: str
    size_kb: int
    file_count: int
    output_path: str
    processing_status: Optional[str] = "pending"


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


@public_router.get("/folder_state", response_model=QueryResult)
async def get_folder_state_public(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    x_mission_password: Optional[str] = Header(None, description="Password for protected missions"),
):
    """Get folder state information (Public API - enforces password protection)"""
    result = await get_folder_state_internal(limit, offset)
    result.data = filter_protected_missions(result.data, x_mission_password)
    result.count = len(result.data)
    return result


@internal_router.get("/folder_state", response_model=QueryResult)
async def get_folder_state_internal(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get folder state information (Internal API - no password protection)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query with new schema
    query = """
    SELECT
      folder_key,
      mission_key,
      fp,
      output_path,
      size_kb,
      file_count,
      last_checked,
      last_processed,
      processing_time,
      processing_status,
      error_message,
      detailed_error_message,
      datetime(last_checked,'unixepoch') AS last_checked_time,
      datetime(last_processed,'unixepoch') AS last_processed_time
    FROM folder_state
    ORDER BY last_checked DESC
    LIMIT ? OFFSET ?
    """

    # Execute query
    cursor.execute(query, (limit, offset))
    rows = cursor.fetchall()

    # Get total count
    cursor.execute("SELECT COUNT(*) as count FROM folder_state")
    count = cursor.fetchone()["count"]

    conn.close()

    # Convert rows to list of dicts - no password filtering for internal API
    data = [dict(row) for row in rows]

    return QueryResult(data=data, count=count)


@public_router.get("/folder_state/{folder_key:path}", response_model=Dict[str, Any])
async def get_folder_state_by_key_public(
    folder_key: str,
    x_mission_password: Optional[str] = Header(None, description="Password for protected missions"),
):
    """Get folder state for folder_key (Public API - enforces password protection)."""
    result = await get_folder_state_by_key_internal(folder_key)
    mission_key = result.get("mission_key")

    if mission_key and is_mission_protected(mission_key):
        if not x_mission_password or not validate_mission_password(mission_key, x_mission_password):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Mission is password protected",
                    "mission_key": mission_key,
                    "protected": True,
                },
            )

    return result


@internal_router.get("/folder_state/{folder_key:path}", response_model=Dict[str, Any])
async def get_folder_state_by_key_internal(folder_key: str):
    """Get folder state for folder_key (Internal API - no password protection)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query for exact match
    query = """
    SELECT
      folder_key,
      mission_key,
      fp,
      output_path,
      size_kb,
      file_count,
      last_checked,
      last_processed,
      processing_time,
      processing_status,
      error_message,
      detailed_error_message,
      datetime(last_checked,'unixepoch') AS last_checked_time,
      datetime(last_processed,'unixepoch') AS last_processed_time
    FROM folder_state
    WHERE folder_key = ?
    """

    cursor.execute(query, (folder_key,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=404,
            detail=f"Folder state not found for: {folder_key}",
        )

    return dict(row)


@internal_router.put("/folder_state/{folder_key:path}")
async def update_folder_state(folder_key: str, update_data: FolderStateUpdate):
    """Update folder state record (Internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if record exists
    cursor.execute("SELECT folder_key FROM folder_state WHERE folder_key = ?", (folder_key,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Folder state record not found for folder_key: {folder_key}",
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

    # Add folder_key for WHERE clause
    update_values.append(folder_key)

    update_query = f"""
    UPDATE folder_state 
    SET {', '.join(update_fields)}
    WHERE folder_key = ?
    """

    cursor.execute(update_query, update_values)
    conn.commit()

    # Return updated record
    cursor.execute(
        """SELECT folder_key, mission_key, fp, processing_status, 
           processing_time, error_message, detailed_error_message, last_processed 
           FROM folder_state WHERE folder_key = ?""",
        (folder_key,),
    )
    updated_record = cursor.fetchone()
    conn.close()

    return {
        "message": "Folder state updated successfully",
        "record": dict(updated_record),
    }


@public_router.get("/folder_state/prefix/{subpath:path}", response_model=QueryResult)
async def get_folder_state_by_subpath_public(
    subpath: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    x_mission_password: Optional[str] = Header(None, description="Password for protected missions"),
) -> QueryResult:
    """Get folder state for subpath prefix (Public API - enforces password protection)."""
    result = await get_folder_state_by_subpath_internal(subpath, limit, offset)
    result.data = filter_protected_missions(result.data, x_mission_password)
    result.count = len(result.data)
    return result


@internal_router.get("/folder_state/prefix/{subpath:path}", response_model=QueryResult)
async def get_folder_state_by_subpath_internal(
    subpath: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
) -> QueryResult:
    """Get folder state for subpath prefix (Internal API - no password protection)."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Use the subpath as a prefix filter
    filter_value = f"{subpath}%"

    # Query with new schema filtered by subpath
    query = """
    SELECT
      folder_key,
      mission_key,
      fp,
      output_path,
      size_kb,
      file_count,
      last_checked,
      last_processed,
      processing_time,
      processing_status,
      error_message,
      detailed_error_message,
      datetime(last_checked,'unixepoch') AS last_checked_time,
      datetime(last_processed,'unixepoch') AS last_processed_time
    FROM folder_state
    WHERE folder_key LIKE ?
    ORDER BY last_checked DESC
    LIMIT ? OFFSET ?
    """

    # Execute query with subpath filter
    cursor.execute(query, (filter_value, limit, offset))
    rows = cursor.fetchall()

    # Get total count for the filtered subpath
    count_query = """
    SELECT COUNT(*) as count FROM folder_state WHERE folder_key LIKE ?
    """
    cursor.execute(count_query, (filter_value,))
    count = cursor.fetchone()["count"]

    conn.close()

    # Convert rows to list of dictionaries - no password filtering for internal API
    data = [dict(row) for row in rows]

    return QueryResult(data=data, count=count)


@public_router.get("/mission_folders/{mission_key:path}", response_model=QueryResult)
@internal_router.get("/mission_folders/{mission_key:path}", response_model=QueryResult)
async def get_folder_state_by_mission(
    mission_key: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    x_mission_password: Optional[str] = Header(None, description="Password for protected missions"),
) -> QueryResult:
    """Get folder state information for a specific mission key.
    Protected missions require valid password via x-mission-password header.
    """
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

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query filtered by mission_key
    query = """
    SELECT
      folder_key,
      mission_key,
      fp,
      output_path,
      size_kb,
      file_count,
      last_checked,
      last_processed,
      processing_time,
      processing_status,
      error_message,
      detailed_error_message,
      datetime(last_checked,'unixepoch') AS last_checked_time,
      datetime(last_processed,'unixepoch') AS last_processed_time
    FROM folder_state
    WHERE mission_key = ?
    ORDER BY last_checked DESC
    LIMIT ? OFFSET ?
    """

    # Execute query with mission_key filter
    cursor.execute(query, (mission_key, limit, offset))
    rows = cursor.fetchall()

    # Get total count for the mission
    count_query = """
    SELECT COUNT(*) as count FROM folder_state WHERE mission_key = ?
    """
    cursor.execute(count_query, (mission_key,))
    count = cursor.fetchone()["count"]

    conn.close()

    # Convert rows to list of dictionaries
    data = [dict(row) for row in rows]

    return QueryResult(data=data, count=count)


@internal_router.post("/folder_state", response_model=Dict[str, Any])
async def create_folder_state(create_data: FolderStateCreate):
    """Create new folder state record (Internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    current_time = int(time.time())

    try:
        cursor.execute(
            """INSERT INTO folder_state
            (folder_key, mission_key, fp, size_kb, file_count, last_checked, last_processed, processing_status, output_path)
            VALUES (?, ?, ?, ?, ?, ?, NULL, ?, ?)
            ON CONFLICT(folder_key) DO UPDATE SET
            mission_key = excluded.mission_key,
            fp = excluded.fp,
            size_kb = excluded.size_kb,
            file_count = excluded.file_count,
            last_checked = excluded.last_checked,
            last_processed = NULL,
            processing_status = excluded.processing_status,
            output_path = excluded.output_path""",
            (
                create_data.folder_key,
                create_data.mission_key,
                create_data.fingerprint,
                create_data.size_kb,
                create_data.file_count,
                current_time,
                create_data.processing_status,
                create_data.output_path,
            ),
        )
        conn.commit()

        # Return created record
        cursor.execute(
            """SELECT folder_key, mission_key, fp, processing_status, 
               size_kb, file_count, last_checked FROM folder_state WHERE folder_key = ?""",
            (create_data.folder_key,),
        )
        created_record = cursor.fetchone()
        conn.close()

        return {
            "message": "Folder state created successfully",
            "record": dict(created_record),
        }
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=f"Error creating folder state: {str(e)}")


@internal_router.patch("/folder_state/{folder_key:path}/last_checked", response_model=Dict[str, Any])
async def update_folder_state_last_checked(folder_key: str):
    """Update only the last_checked timestamp for folder state (Internal use only)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if record exists
    cursor.execute(
        "SELECT folder_key FROM folder_state WHERE folder_key = ?",
        (folder_key,),
    )
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(
            status_code=404,
            detail=f"Folder state record not found for folder_key: {folder_key}",
        )

    # Update only last_checked timestamp
    current_time = int(time.time())
    cursor.execute(
        "UPDATE folder_state SET last_checked = ? WHERE folder_key = ?",
        (current_time, folder_key),
    )
    conn.commit()

    # Return updated record
    cursor.execute(
        """SELECT folder_key, mission_key, fp, processing_status, 
           processing_time, error_message, detailed_error_message, last_checked 
           FROM folder_state WHERE folder_key = ?""",
        (folder_key,),
    )
    updated_record = cursor.fetchone()
    conn.close()

    return {
        "message": "Folder state last_checked updated successfully",
        "record": dict(updated_record),
    }
