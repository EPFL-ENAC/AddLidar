"""
API client functions for communicating with the backend API.
"""

import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class APIClient:
    """Client for backend API operations"""

    def __init__(self, backend_url: str):
        self.backend_url = backend_url

    def get_folder_state(self, folder_key: str) -> Optional[Dict]:
        """Get folder state from API by folder key"""
        try:
            url = f"{self.backend_url}/sqlite/folder_state/{folder_key}"
            response = requests.get(url, timeout=30)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            data = response.json()
            # Return first record if available
            if data.get("data") and len(data["data"]) > 0:
                return data["data"][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching folder state for {folder_key}: {e}")
            return None

    def check_mission_exists(self, mission_key: str) -> bool:
        """Check if mission exists in folder_state via API"""
        try:
            url = f"{self.backend_url}/sqlite/folder_state/mission/{mission_key}"
            response = requests.get(url, timeout=30)
            if response.status_code == 404:
                return False
            response.raise_for_status()
            data = response.json()
            return data.get("count", 0) > 0
        except Exception as e:
            logger.error(f"Error checking mission existence for {mission_key}: {e}")
            return False

    def get_potree_metacloud_state(self, mission_key: str) -> Optional[Dict]:
        """Get potree metacloud state from API by mission key"""
        try:
            url = f"{self.backend_url}/sqlite/potree_metacloud_state/{mission_key}"
            response = requests.get(url, timeout=30)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(
                f"Error fetching potree metacloud state for {mission_key}: {e}"
            )
            return None

    def create_folder_state(
        self,
        folder_key: str,
        mission_key: str,
        fp: str,
        size: int,
        count: int,
        output_path: str,
    ) -> bool:
        """Create or update folder state via API"""
        try:
            # First try to update existing record via API
            url = f"{self.backend_url}/sqlite/folder_state/{folder_key}"
            payload = {"fingerprint": fp, "processing_status": "pending"}
            response = requests.put(url, json=payload, timeout=30)

            if response.status_code == 404:
                # Record doesn't exist - create it via API
                logger.info(
                    f"Creating new folder state record via API for {folder_key}"
                )
                create_url = f"{self.backend_url}/sqlite/folder_state"
                create_payload = {
                    "folder_key": folder_key,
                    "mission_key": mission_key,
                    "fingerprint": fp,
                    "size_kb": size,
                    "file_count": count,
                    "output_path": output_path,
                    "processing_status": "pending",
                }
                create_response = requests.post(
                    create_url, json=create_payload, timeout=30
                )
                create_response.raise_for_status()
                return True

            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error creating/updating folder state for {folder_key}: {e}")
            return False

    def create_potree_metacloud_state(
        self, mission_key: str, fp: str, output_path: str
    ) -> bool:
        """Create or update potree metacloud state via API"""
        try:
            # Try to update existing record via API
            url = f"{self.backend_url}/sqlite/potree_metacloud_state/{mission_key}"
            payload = {"fingerprint": fp, "processing_status": "pending"}
            response = requests.put(url, json=payload, timeout=30)

            if response.status_code == 404:
                # Record doesn't exist - create it via API
                logger.info(
                    f"Creating new potree metacloud state record via API for {mission_key}"
                )
                create_url = f"{self.backend_url}/sqlite/potree_metacloud_state"
                create_payload = {
                    "mission_key": mission_key,
                    "fingerprint": fp,
                    "output_path": output_path,
                    "processing_status": "pending",
                }
                create_response = requests.post(
                    create_url, json=create_payload, timeout=30
                )
                create_response.raise_for_status()
                return True

            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(
                f"Error creating/updating potree metacloud state for {mission_key}: {e}"
            )
            return False

    def update_potree_metacloud_last_checked(self, mission_key: str) -> bool:
        """Update only the last_checked timestamp for potree metacloud state"""
        try:
            url = f"{self.backend_url}/sqlite/potree_metacloud_state/{mission_key}/last_checked"
            response = requests.patch(url, timeout=30)
            if response.status_code == 404:
                logger.warning(
                    f"Potree metacloud state not found for mission {mission_key}"
                )
                return False
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(
                f"Error updating last_checked for potree metacloud state {mission_key}: {e}"
            )
            return False
