from fastapi import APIRouter
from typing import Dict, Any


from .base import get_db_connection, QueryResult, logger
from .folder_state import (
    public_router as folder_state_public,
    internal_router as folder_state_internal,
)
from .potree_metacloud_state import (
    public_router as potree_metacloud_public,
    internal_router as potree_metacloud_internal,
)
from .base import (
    public_router as general_public,
    internal_router as general_internal,
)

# Import settings
from src.config.settings import settings


# Create main routers with original prefix to maintain compatibility
public_router = APIRouter(
    prefix="/sqlite",
    tags=["sqlite"],
    responses={404: {"description": "Not found"}},
)

internal_router = APIRouter(
    prefix="/sqlite",
    tags=["sqlite-internal"],
    responses={404: {"description": "Not found"}},
)

# Include sub-routers
public_router.include_router(general_public)
public_router.include_router(folder_state_public)
public_router.include_router(potree_metacloud_public)

internal_router.include_router(general_internal)
internal_router.include_router(folder_state_internal)
internal_router.include_router(potree_metacloud_internal)


# Shared endpoints that combine data from both tables
@public_router.get("/processing_status", response_model=QueryResult)
@internal_router.get("/processing_status", response_model=QueryResult)
async def get_processing_status():
    """Get processing status overview for both folder_state and potree_metacloud_state"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Combined query to get processing status overview
    query = """
    SELECT 
      'folder_state' as table_name,
      processing_status,
      COUNT(*) as count
    FROM folder_state 
    GROUP BY processing_status
    
    UNION ALL
    
    SELECT 
      'potree_metacloud_state' as table_name,
      processing_status,
      COUNT(*) as count
    FROM potree_metacloud_state 
    GROUP BY processing_status
    
    ORDER BY table_name, processing_status
    """

    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()

    # Convert rows to list of dicts
    data = [dict(row) for row in rows]
    count = len(data)

    return QueryResult(data=data, count=count)


@public_router.get("/settings", response_model=Dict[str, Any])
@internal_router.get("/settings", response_model=Dict[str, Any])
async def get_settings():
    """Get current settings"""
    # Convert settings to dictionary
    settings_dict = settings.model_dump()
    return {"settings": settings_dict}
