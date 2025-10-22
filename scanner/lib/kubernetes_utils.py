"""Kubernetes utilities and job management."""

## WARNING : IF YOU UPDATE THIS FILE UPDATE THE ONE IN BACKEND/LIDAR-API/SRC/UTILS/KUBERNETES_UTILS.PY TOO ##

import os
import logging
import subprocess
import sys
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime

try:
    from kubernetes import client, config, utils
    import jinja2
    import yaml
except ImportError:
    print("Error: required modules not found.")
    sys.exit(1)

logger = logging.getLogger(__name__)


def get_current_namespace() -> str:
    """Get the current Kubernetes namespace where the scanner is running."""
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

    logger.warning("Could not detect namespace, using 'default'")
    return "default"


def get_node_scheduling_config() -> Tuple[Optional[List[Dict]], Optional[Dict]]:
    """Get node scheduling configuration based on current environment."""
    current_namespace = get_current_namespace()

    # Check if this is a production environment that should use RCP HAAS nodes
    if current_namespace == "epfl-eso-addlidar-prod":
        logger.info(
            "Detected production environment - configuring jobs for RCP HAAS nodes"
        )
        tolerations = [
            {
                "key": "dedicated",
                "value": "rcpHAAS",
                "operator": "Equal",
                "effect": "NoExecute",
            }
        ]
        node_selector = {"rcpnas3": "available"}
        return tolerations, node_selector
    else:
        logger.info(
            f"Standard environment detected ({current_namespace}) - no special node scheduling required"
        )
        return None, None


def get_resource_config_from_env() -> Dict[str, str]:
    """Read resource configuration from environment variables."""
    return {
        "compression_cpu_request": os.environ.get("COMPRESSION_CPU_REQUEST", "500m"),
        "compression_memory_request": os.environ.get(
            "COMPRESSION_MEMORY_REQUEST", "1Gi"
        ),
        "compression_cpu_limit": os.environ.get("COMPRESSION_CPU_LIMIT", "2"),
        "compression_memory_limit": os.environ.get("COMPRESSION_MEMORY_LIMIT", "4Gi"),
        "potree_cpu_request": os.environ.get("POTREE_CPU_REQUEST", "1"),
        "potree_memory_request": os.environ.get("POTREE_MEMORY_REQUEST", "2Gi"),
        "potree_cpu_limit": os.environ.get("POTREE_CPU_LIMIT", "4"),
        "potree_memory_limit": os.environ.get("POTREE_MEMORY_LIMIT", "8Gi"),
    }


def create_kubernetes_job(
    template_path: str, context: Dict[str, Any], export_only: bool = False
) -> Optional[int]:
    """Create a Kubernetes job from a Jinja2 template."""
    try:
        if not os.path.exists(template_path):
            logger.error(f"Template file not found at {template_path}")
            return None

        with open(template_path, "r") as f:
            template_content = f.read()

        template = jinja2.Template(template_content)
        job_yaml = template.render(**context)

        if export_only:
            print(job_yaml)
            return 1

        job_dict = yaml.safe_load(job_yaml)
        result = utils.create_from_dict(client.ApiClient(), job_dict, True)
        job_name = job_dict["metadata"]["name"]
        logger.info(f"Created job '{job_name}'")
        logger.debug(f"Job creation result: {result}")
        return 1

    except Exception as e:
        logger.error(f"Failed to create Kubernetes job: {e}")
        return None
