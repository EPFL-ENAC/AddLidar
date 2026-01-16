"""
Keycloak authentication service for AddLidar API.

This module provides authentication and authorization using Keycloak SSO.
Users must be authenticated via the master Keycloak realm to access protected endpoints.
"""

from enacit4r_auth.services.auth import KeycloakService
from src.config.settings import settings

# Validate required settings
if not settings.KEYCLOAK_API_SECRET:
    raise ValueError("KEYCLOAK_API_SECRET is required")

# Initialize Keycloak service
kc_service = KeycloakService(
    settings.KEYCLOAK_URL,
    settings.KEYCLOAK_REALM,
    settings.KEYCLOAK_API_ID,
    settings.KEYCLOAK_API_SECRET,
    "admin",  # Default role required for authentication
)
