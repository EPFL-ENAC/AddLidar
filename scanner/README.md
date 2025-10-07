# LiDAR Archive Scanner

## Overview

The LiDAR Archive Scanner is a Python-based application designed to scan directories containing LiDAR data and queue Kubernetes jobs for creating compressed archives and Potree conversions. It utilizes Kubernetes for job management and a backend API for state tracking.

## Architecture

The scanner is organized into modular components:

```
scanner/
├── scanner.py              # Main entry point and CLI handling
├── lib/                    # Core modules
│   ├── __init__.py
│   ├── api_client.py       # Backend API communication
│   ├── filesystem.py       # File operations and fingerprinting
│   ├── kubernetes_utils.py # Kubernetes job management
│   └── scanner.py          # Directory scanning logic
├── job-batch-compression.template.yaml    # Kubernetes job template for compression
├── job-batch-potree-converter.template.yaml # Kubernetes job template for Potree conversion
└── Dockerfile              # Container image definition
```

### Core Components

- **`scanner.py`** - Main entry point that handles CLI arguments and orchestrates the scanning process
- **`lib/api_client.py`** - Manages all communication with the backend API for state tracking
- **`lib/filesystem.py`** - Handles file operations, directory fingerprinting, and statistics collection
- **`lib/kubernetes_utils.py`** - Kubernetes configuration and job creation utilities
- **`lib/scanner.py`** - Core scanning logic for detecting changes in directories and metacloud files

## Features

- **Directory Change Detection**: Monitors LiDAR data directories for changes using file fingerprinting
- **Metacloud File Processing**: Scans for `.metacloud` files and queues Potree conversion jobs
- **Batch Job Processing**: Creates Kubernetes batch jobs for efficient parallel processing
- **State Tracking**: Maintains processing state via backend API to avoid duplicate work
- **Environment-aware Scheduling**: Automatically configures jobs for RCP-HAAS or standard environments
- **Dry Run Mode**: Test changes without actually creating jobs or updating state

## Usage

### Command Line Options

```bash
python scanner.py [OPTIONS]

Options:
  --original-root PATH      Root directory containing original LiDAR data (default: ./original_root)
  --zip-root PATH          Root directory for compressed archives (default: ./zip_root)
  --log-level LEVEL        Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL (default: INFO)
  --fts-addlidar-pvc NAME  PVC name for FTS AddLidar (default: fts-addlidar)
  --backend-url URL        Backend API URL for database updates (default: http://backend-internal)
  --dry-run                Check for changes without modifying database or queueing jobs
  --export-only            Print job YAMLs instead of creating them
  --max-jobs INT           Stop after specified number of jobs (0 for unlimited, default: 0)
  --parallelism INT        Number of parallel jobs in batch mode (default: 4)
```

### Examples

```bash
# Standard scan with default settings
python scanner.py --original-root /lidar --zip-root /zips

# Dry run to see what would be processed
python scanner.py --dry-run --log-level DEBUG

# Export job YAML without creating jobs
python scanner.py --export-only

# Limit processing to 10 jobs
python scanner.py --max-jobs 10 --parallelism 2
```

## Docker Usage

Build and run the container:

```bash
docker build -t lidar-scanner .
docker run -v /path/to/lidar:/lidar -v /path/to/zips:/zips lidar-scanner
```

## Environment Variables

### Resource Configuration

- `COMPRESSION_CPU_REQUEST` - CPU request for compression jobs (default: 500m)
- `COMPRESSION_MEMORY_REQUEST` - Memory request for compression jobs (default: 1Gi)
- `COMPRESSION_CPU_LIMIT` - CPU limit for compression jobs (default: 2)
- `COMPRESSION_MEMORY_LIMIT` - Memory limit for compression jobs (default: 4Gi)
- `POTREE_CPU_REQUEST` - CPU request for Potree jobs (default: 1)
- `POTREE_MEMORY_REQUEST` - Memory request for Potree jobs (default: 2Gi)
- `POTREE_CPU_LIMIT` - CPU limit for Potree jobs (default: 4)
- `POTREE_MEMORY_LIMIT` - Memory limit for Potree jobs (default: 8Gi)

### Container Images

- `COMPRESSION_IMAGE_REGISTRY` - Registry for compression image
- `COMPRESSION_IMAGE_NAME` - Name of compression image
- `COMPRESSION_IMAGE_TAG` - Tag for compression image
- `COMPRESSION_IMAGE_SHA256` - SHA256 hash for compression image
- `POTREE_CONVERTER_IMAGE_REGISTRY` - Registry for Potree converter image
- `POTREE_CONVERTER_IMAGE_NAME` - Name of Potree converter image
- `POTREE_CONVERTER_IMAGE_TAG` - Tag for Potree converter image
- `POTREE_CONVERTER_IMAGE_SHA256` - SHA256 hash for Potree converter image

## Dependencies

- `kubernetes` - Kubernetes Python client
- `requests` - HTTP library for API communication
- `pydantic` - Data validation
- `jinja2` - Template engine for Kubernetes job definitions
- `sqlite-utils` - SQLite utilities (legacy dependency)

## Kubernetes Integration

The scanner creates two types of Kubernetes batch jobs:

1. **Compression Jobs** - Process changed directories and create compressed archives
2. **Potree Conversion Jobs** - Convert metacloud files to Potree format

Jobs are configured with:

- Anti-affinity rules to distribute across nodes
- Resource limits and requests
- Automatic retry and timeout policies
- Environment-specific node scheduling (RCP-HAAS support)

## Important Notes

1. **Namespace Configuration**: The namespace is dynamically detected from the current Kubernetes context or service account
2. **State Persistence**: All processing state is maintained via the backend API to ensure consistency
3. **Fingerprinting**: Directory changes are detected using SHA256 fingerprints of file metadata
4. **Batch Processing**: Multiple folders/files are processed in parallel using Kubernetes indexed jobs

## Logging

The scanner provides detailed logging at multiple levels:

- **INFO**: General operation status and progress
- **DEBUG**: Detailed fingerprinting and API communication
- **WARNING**: Non-fatal issues like missing directories
- **ERROR**: Failures that prevent processing

All logs include timestamps and structured formatting for easy parsing.
