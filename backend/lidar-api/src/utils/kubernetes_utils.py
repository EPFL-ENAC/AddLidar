"""Kubernetes utilities for namespace detection."""

## WARNING : IF YOU UPDATE THIS FILE UPDATE THE ONE IN SCANNER/LIB/KUBERNETES_UTILS.PY TOO ##

import os
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)


def get_current_namespace() -> str:
    """
    Get the current Kubernetes namespace where the application is running.

    This function tries multiple methods to detect the current namespace:
    1. Read from service account (when running inside a Kubernetes pod)
    2. Use kubectl to get the current context namespace
    3. Fall back to 'default' namespace

    Returns:
        str: The detected namespace or 'default' as fallback
    """
    # Method 1: Try to read from service account (when running in a pod)
    try:
        if os.path.exists("/var/run/secrets/kubernetes.io/serviceaccount/namespace"):
            with open(
                "/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r"
            ) as f:
                namespace = f.read().strip()
                logger.info(
                    f"Detected current namespace from service account: {namespace}"
                )
                return namespace
    except Exception as e:
        logger.warning(f"Failed to read namespace from service account: {e}")

    # Method 2: Try to get namespace from kubectl context
    try:
        result = subprocess.run(
            [
                "kubectl",
                "config",
                "view",
                "--minify",
                "--output",
                "jsonpath={..namespace}",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            namespace = result.stdout.strip()
            logger.info(f"Detected current namespace from kubectl context: {namespace}")
            return namespace
    except Exception as e:
        logger.warning(f"Failed to get namespace from kubectl: {e}")

    # Method 3: Fall back to default namespace
    logger.warning("Could not detect namespace, using 'default'")
    return "default"


def get_namespace_with_fallback(configured_namespace: Optional[str] = None) -> str:
    """
    Get the namespace to use, with runtime detection as fallback.

    Args:
        configured_namespace: Explicitly configured namespace (from settings)

    Returns:
        str: The namespace to use
    """
    if configured_namespace and configured_namespace.strip():
        logger.info(f"Using configured namespace: {configured_namespace}")
        return configured_namespace

    return get_current_namespace()
