"""
Configuration module for the scanner application.
"""

import os
import logging


# Configure logging
def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
    return logging.getLogger("scanner.py")


# Global configuration that will be set by main
class Config:
    def __init__(self):
        self.ORIG: str = ""
        self.ZIP: str = ""
        self.FTS_ADDLIDAR_PVC: str = ""
        self.BACKEND_URL: str = ""
        self.args = None

    def update_from_args(self, args):
        """Update configuration from parsed arguments"""
        self.ORIG = args.original_root
        self.ZIP = args.zip_root
        self.FTS_ADDLIDAR_PVC = args.fts_addlidar_pvc
        self.BACKEND_URL = args.backend_url
        self.args = args


# Global config instance
config = Config()
