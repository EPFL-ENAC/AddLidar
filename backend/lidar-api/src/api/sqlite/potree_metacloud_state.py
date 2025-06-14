from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, Optional
import time

from .base import get_db_connection, QueryResult, logger


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


class PotreeMetacloudStateUpdate(BaseModel):
    fingerprint: Optional[str] = None
    processing_status: Optional[str]  # 'success', 'failed', 'empty'
    processing_time: Optional[int] = None
    error_message: Optional[str] = None


# Create routers
public_router = APIRouter()
internal_router = APIRouter()


@public_router.get("/potree_metacloud_state", response_model=QueryResult)
@internal_router.get("/potree_metacloud_state", response_model=QueryResult)
async def get_potree_metacloud_state(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """Get potree metacloud state information"""
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


@internal_router.put(
    "/potree_metacloud_state/{mission_key:path}", response_model=Dict[str, Any]
)
async def update_potree_metacloud_state(
    mission_key: str, update_data: PotreeMetacloudStateUpdate
):
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
           processing_time, error_message, last_processed 
           FROM potree_metacloud_state WHERE mission_key = ?""",
        (mission_key,),
    )
    updated_record = cursor.fetchone()
    conn.close()

    return {
        "message": "Potree metacloud state updated successfully",
        "record": dict(updated_record),
    }


@public_router.get(
    "/potree_metacloud_state/{mission_key}", response_model=Dict[str, Any]
)
@internal_router.get(
    "/potree_metacloud_state/{mission_key}", response_model=Dict[str, Any]
)
async def get_potree_metacloud_state_by_mission(mission_key: str):
    """Get potree metacloud state for a specific mission"""
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
