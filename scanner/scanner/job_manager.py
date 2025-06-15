"""
Kubernetes job management for compression and Potree conversion tasks.
"""

import logging
import os
import yaml
from datetime import datetime
from typing import List, Optional

import jinja2
from kubernetes import client, utils

from .config import config

logger = logging.getLogger(__name__)


class JobManager:
    """Manager for Kubernetes job creation and execution"""

    def __init__(self):
        self.script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def queue_potree_conversion_jobs(
        self, metacloud_files: List[List[str]], export_only: bool = False
    ) -> Optional[int]:
        """
        Create a Kubernetes batch job for Potree conversion of metacloud files using a template.

        Args:
            metacloud_files: List containing [mission_key, metacloud_path, fingerprint] lists
            export_only: Whether to only export the job YAML without creating it

        Returns:
            Optional[int]: Number of jobs created (1 if batch job created) or None if no action was taken
        """
        if not metacloud_files:
            logger.info("No metacloud files to process, skipping job creation")
            return None

        try:
            # Load Jinja2 template
            template_path = os.path.join(
                self.script_dir,
                "job-batch-potree-converter.template.yaml",
            )

            if not os.path.exists(template_path):
                logger.error(f"Potree template file not found at {template_path}")
                return None

            with open(template_path, "r") as f:
                template_content = f.read()

            # Setup Jinja2 environment
            template = jinja2.Template(template_content)

            # Generate timestamp for unique job name
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Prepare template context
            parallelism = min(
                len(metacloud_files), 4
            )  # Limit parallelism based on number of files

            context = {
                "timestamp": timestamp,
                "metacloud_files": metacloud_files,
                "parallelism": parallelism,
                "fts_addlidar_pvc_name": config.FTS_ADDLIDAR_PVC,
                "backend_url": config.BACKEND_URL,
                "potree_converter_image_registry": os.environ.get(
                    "POTREE_CONVERTER_IMAGE_REGISTRY"
                ),
                "potree_converter_image_name": os.environ.get(
                    "POTREE_CONVERTER_IMAGE_NAME"
                ),
                "potree_converter_image_tag": os.environ.get(
                    "POTREE_CONVERTER_IMAGE_TAG"
                ),
                "potree_converter_image_sha256": os.environ.get(
                    "POTREE_CONVERTER_IMAGE_SHA256"
                ),
            }

            # Render the template
            job_yaml = template.render(**context)

            if export_only:
                print(job_yaml)
                logger.info(
                    f"Printed batch Potree job YAML for {len(metacloud_files)} metacloud files"
                )
                return 1

            # Create job from YAML
            job_dict = yaml.safe_load(job_yaml)
            try:
                result = utils.create_from_dict(client.ApiClient(), job_dict, True)
                job_name = job_dict["metadata"]["name"]
                logger.info(
                    f"Created batch Potree conversion job '{job_name}' for {len(metacloud_files)} metacloud files"
                )
                logger.debug(f"Job creation result: {result}")
                return 1
            except Exception as api_ex:
                logger.error(f"Failed to create Kubernetes batch job via API: {api_ex}")
                return None

        except Exception as e:
            logger.error(f"Failed to create Potree conversion batch job: {e}")
            return None

    def queue_batch_zip_job(
        self, folders: List[List[str]], export_only: bool = False
    ) -> Optional[int]:
        """
        Create a single batch Kubernetes job to process multiple folders.

        Args:
            folders: List of relative folder paths to archive with their fingerprints [rel, fp]
            export_only: Whether to only export the job YAML without creating it

        Returns:
            Optional[int]: Number of folders processed or None if no action was taken
        """
        if not folders:
            logger.info("No folders to process, skipping batch job creation")
            return None

        # Generate timestamp for unique job name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

        try:
            # Load Jinja2 template
            template_path = os.path.join(
                self.script_dir,
                "job-batch-compression.template.yaml",
            )

            if not os.path.exists(template_path):
                logger.error(f"Template file not found at {template_path}")
                return None

            with open(template_path, "r") as f:
                template_content = f.read()

            # Setup Jinja2 environment
            template = jinja2.Template(template_content)

            # Prepare template variables
            context = {
                "folders": folders,
                "timestamp": timestamp,
                "parallelism": config.args.parallelism,
                "orig_dir": config.ORIG,
                "zip_dir": config.ZIP,
                "fts_addlidar_pvc_name": config.FTS_ADDLIDAR_PVC,
                "backend_url": config.BACKEND_URL,
                "compression_image_registry": os.environ.get(
                    "COMPRESSION_IMAGE_REGISTRY"
                ),
                "compression_image_name": os.environ.get("COMPRESSION_IMAGE_NAME"),
                "compression_image_tag": os.environ.get("COMPRESSION_IMAGE_TAG"),
                "compression_image_sha256": os.environ.get("COMPRESSION_IMAGE_SHA256"),
            }

            # Render the template
            job_yaml = template.render(**context)

            if export_only:
                print(job_yaml)
                logger.info(f"Printed batch job YAML for {len(folders)} folders")
                return len(folders)

            # Create job from YAML
            job_dict = yaml.safe_load(job_yaml)
            try:
                result = utils.create_from_dict(client.ApiClient(), job_dict, True)
                job_name = job_dict["metadata"]["name"]
                logger.info(
                    f"Created batch job '{job_name}' for {len(folders)} folders"
                )
                logger.debug(f"Job creation result: {result}")
                return len(folders)
            except Exception as api_ex:
                logger.error(f"Failed to create Kubernetes job via API: {api_ex}")
                raise
        except Exception as e:
            logger.error(f"Failed to create batch job: {e}")
            raise
