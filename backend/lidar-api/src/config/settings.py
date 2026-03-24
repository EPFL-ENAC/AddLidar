from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Allow extra fields in .env that aren't defined in Settings
    )

    IMAGE_NAME: str = "lvjospinepfl/lidardatamanager"
    IMAGE_TAG: str = "latest"
    PATH_PREFIX: str = "/api"
    NAMESPACE: Optional[str] = None  # If None, will use runtime detection
    MOUNT_PATH: str = "/data"
    SUB_PATH: str = "fts-addlidar/LiDAR"
    DATABASE_PATH: str = "./data/database.db"  # Default path for SQLite database
    OUTPUT_PATH: str = "/output"
    PVC_OUTPUT_NAME: str = "lidar-data-output-pvc"  # Default to our created PVC
    PVC_NAME: str = "lidar-data-pvc"  # Default to our created PVC
    ENVIRONMENT: str = "development"  # "development" or "production"
    JOB_TIMEOUT: int = 300  # Timeout in seconds for job completion
    DEFAULT_OUTPUT_ROOT: str = "/output"  # Default root path based on environment

    # Keycloak configuration
    KEYCLOAK_REALM: str = "master"
    KEYCLOAK_URL: str = "https://enac-it-sso2.epfl.ch"
    KEYCLOAK_API_ID: str = "addlidar-api"
    KEYCLOAK_API_SECRET: str = "not-used-for-jwt-validation"  # Not used for token validation, only for admin operations

    @property
    def effective_namespace(self) -> str:
        """Get the effective namespace to use, with runtime detection if not configured."""
        if self.NAMESPACE:
            return self.NAMESPACE

        # Import here to avoid circular imports
        from src.utils.kubernetes_utils import get_current_namespace

        return get_current_namespace()

    @property
    def is_rcp_haas(self) -> bool:
        """Check if running in RCP-HAAS environment."""
        return "rcp-haas" in self.effective_namespace.lower()


settings = Settings()
