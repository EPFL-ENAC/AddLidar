import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class APIClient:
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
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching folder state for {folder_key}: {e}")
            return None

    def check_mission_exists(self, mission_key: str) -> bool:
        """Check if mission exists in folder_state via API"""
        try:
            url = f"{self.backend_url}/sqlite/mission_folders/{mission_key}"
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
            url = f"{self.backend_url}/sqlite/folder_state/{folder_key}"
            payload = {"fingerprint": fp, "processing_status": "pending"}
            response = requests.put(url, json=payload, timeout=30)

            if response.status_code == 404:
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

    def create_folder_state_empty(
        self,
        folder_key: str,
        mission_key: str,
        fp: str,
        size: int,
        count: int,
        output_path: str,
    ) -> bool:
        """Create or update folder state for empty folders with 'empty' status"""
        try:
            url = f"{self.backend_url}/sqlite/folder_state/{folder_key}"
            payload = {
                "fingerprint": fp,
                "processing_status": "empty",
                "processing_time": 0,
                "error_message": "Folder is empty (no files)",
            }
            response = requests.put(url, json=payload, timeout=30)

            if response.status_code == 404:
                logger.info(
                    f"Creating new folder state record for empty folder via API: {folder_key}"
                )
                create_url = f"{self.backend_url}/sqlite/folder_state"
                create_payload = {
                    "folder_key": folder_key,
                    "mission_key": mission_key,
                    "fingerprint": fp,
                    "size_kb": size,
                    "file_count": count,
                    "output_path": output_path,
                    "processing_status": "empty",
                    "processing_time": 0,
                    "error_message": "Folder is empty (no files)",
                }
                create_response = requests.post(
                    create_url, json=create_payload, timeout=30
                )
                create_response.raise_for_status()
                return True

            response.raise_for_status()
            logger.info(f"Marked folder as empty: {folder_key}")
            return True
        except Exception as e:
            logger.error(
                f"Error creating/updating empty folder state for {folder_key}: {e}"
            )
            return False

    def create_potree_metacloud_state(
        self,
        mission_key: str,
        fp: str,
        output_path: str,
        metacloud_filename: str = None,
        name: str = None,
        date: str = None,
        extra_attributes: str = None,
    ) -> bool:
        """Create or update potree metacloud state via API"""
        try:
            url = f"{self.backend_url}/sqlite/potree_metacloud_state/{mission_key}"
            payload = {"fingerprint": fp, "processing_status": "pending"}
            if metacloud_filename:
                payload["metacloud_filename"] = metacloud_filename
            if name is not None:
                payload["name"] = name
            if date is not None:
                payload["date"] = date
            if extra_attributes is not None:
                payload["extra_attributes"] = extra_attributes
            response = requests.put(url, json=payload, timeout=30)

            if response.status_code == 404:
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
                if metacloud_filename:
                    create_payload["metacloud_filename"] = metacloud_filename
                if name:
                    create_payload["name"] = name
                if date:
                    create_payload["date"] = date
                if extra_attributes:
                    create_payload["extra_attributes"] = extra_attributes
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

    def update_potree_metacloud_last_checked(
        self, mission_key: str, metacloud_filename: str = None
    ) -> bool:
        """Update only the last_checked timestamp for potree metacloud state"""
        try:
            url = f"{self.backend_url}/sqlite/potree_metacloud_state/{mission_key}/last_checked"
            payload = {}
            if metacloud_filename:
                payload["metacloud_filename"] = metacloud_filename
            response = requests.patch(url, json=payload, timeout=30)
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

    def update_folder_last_checked(self, folder_key: str) -> bool:
        """Update only the last_checked timestamp for folder state"""
        try:
            url = f"{self.backend_url}/sqlite/folder_state/{folder_key}/last_checked"
            response = requests.patch(url, timeout=30)
            if response.status_code == 404:
                logger.warning(f"Folder state not found for {folder_key}")
                return False
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error updating last_checked for folder {folder_key}: {e}")
            return False

    def get_mission_protection(self, mission_key: str) -> Optional[Dict]:
        """Get mission protection status from API"""
        try:
            url = f"{self.backend_url}/sqlite/mission_protection/{mission_key}"
            response = requests.get(url, timeout=30)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching mission protection for {mission_key}: {e}")
            return None

    def create_mission_protection(self, mission_key: str, password: str) -> bool:
        """Create or update mission protection via API"""
        try:
            url = f"{self.backend_url}/sqlite/mission_protection"
            payload = {"mission_key": mission_key, "password": password}
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error creating mission protection for {mission_key}: {e}")
            return False

    def update_mission_protection_last_checked(self, mission_key: str) -> bool:
        """Update only the last_checked timestamp for mission protection"""
        try:
            url = f"{self.backend_url}/sqlite/mission_protection/{mission_key}/last_checked"
            response = requests.patch(url, timeout=30)
            if response.status_code == 404:
                logger.warning(f"Mission protection not found for {mission_key}")
                return False
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(
                f"Error updating last_checked for mission protection {mission_key}: {e}"
            )
            return False

    def delete_mission_protection(self, mission_key: str) -> bool:
        """Delete mission protection via API"""
        try:
            url = f"{self.backend_url}/sqlite/mission_protection/{mission_key}"
            response = requests.delete(url, timeout=30)
            if response.status_code == 404:
                logger.warning(f"Mission protection not found for {mission_key}")
                return False
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error deleting mission protection for {mission_key}: {e}")
            return False

    def get_all_missions(self) -> Optional[Dict]:
        """Get all missions from potree_metacloud_state"""
        try:
            url = f"{self.backend_url}/sqlite/potree_metacloud_state"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching all missions: {e}")
            return None

    def delete_mission(self, mission_key: str) -> bool:
        """Delete a mission and all its associated data"""
        try:
            url = f"{self.backend_url}/sqlite/mission/{mission_key}"
            response = requests.delete(url, timeout=30)
            if response.status_code == 404:
                logger.warning(f"Mission not found: {mission_key}")
                return False
            response.raise_for_status()
            logger.info(f"Successfully deleted mission {mission_key} from database")
            return True
        except Exception as e:
            logger.error(f"Error deleting mission {mission_key}: {e}")
            return False
