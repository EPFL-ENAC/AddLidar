# Database Snapshot Management

This directory contains tools for managing database snapshots from production environments.

## Quick Start

The easiest way to manage snapshots is using the Makefile commands:

```bash
# List all local snapshots
make snapshot-list

# Download latest snapshot from production
make snapshot-download

# Backup current database
make snapshot-backup

# Switch to a specific snapshot
make snapshot-switch-to SNAPSHOT=./snapshots/snapshot_prod_2025_06_16_120000.db

# Get help
make snapshot-help
```

## Manual Usage

You can also use the snapshot script directly:

```bash
# List local snapshots
./snapshot.sh list

# Download from production (auto-detect pod)
./snapshot.sh download

# Download from specific pod
./snapshot.sh download-pod backend-deployment-abc123

# Switch to snapshot
./snapshot.sh switch ./snapshots/snapshot_prod_2025_06_16_120000.db

# Backup current database
./snapshot.sh backup
```

## Advanced Usage

For more control, use the Python script directly:

```bash
# List snapshots with detailed info
uv run python src/utils/snapshot_manager.py list

# Download from specific namespace and pod
uv run python src/utils/snapshot_manager.py download --pod backend-deployment-abc123 --namespace epfl-eso-addlidar-prod

# Switch without creating backup
uv run python src/utils/snapshot_manager.py switch ./snapshots/snapshot_prod_2025_06_16_120000.db --no-backup
```

## Prerequisites

### For Local Development

1. **uv** - Python package manager
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

### For Production Downloads

1. **kubectl** - Kubernetes command line tool

   ```bash
   # Install kubectl (example for Linux)
   curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
   chmod +x kubectl
   sudo mv kubectl /usr/local/bin/
   ```

2. **Kubernetes cluster access** - Configure kubectl to access your production cluster
   ```bash
   # This depends on your cluster setup
   kubectl config use-context your-production-context
   ```

## How It Works

### Snapshot Downloads

The system works by:

1. **Finding production pods** - Uses `kubectl` to find pods in the production namespace that might contain the database
2. **Copying database files** - Uses `kubectl cp` to copy the SQLite database from the pod to your local machine
3. **Organizing snapshots** - Saves snapshots with timestamps in the `snapshots/` directory

### Snapshot Management

- **Automatic backups** - When switching snapshots, the current database is automatically backed up
- **Timestamp naming** - All snapshots and backups use timestamp-based naming for easy identification
- **Size information** - File sizes are displayed to help identify valid snapshots

## File Structure

```
backend/lidar-api/
├── snapshot.sh                          # Quick access script
├── src/utils/snapshot_manager.py         # Main Python utility
├── snapshots/                           # Directory for all snapshots
│   ├── snapshot_prod_2025_06_16_120000.db
│   ├── backup_local_2025_06_16_130000.db
│   └── ...
└── data/
    └── database.db                      # Current active database
```

## Configuration

### Default Settings

- **Production namespace**: `epfl-eso-addlidar-prod`
- **Remote database path**: `/app/data/database.db`
- **Local database path**: `./data/database.db`
- **Snapshots directory**: `./snapshots/`

### Customization

You can override these settings by modifying the scripts or using command-line arguments:

```bash
# Use different namespace
uv run python src/utils/snapshot_manager.py download --auto --namespace my-custom-namespace

# Specify base directory
uv run python src/utils/snapshot_manager.py --base-dir /path/to/lidar-api list
```

## Troubleshooting

### kubectl not found

```bash
# Install kubectl first
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
```

### No pods found

- Check if kubectl can access your cluster: `kubectl get pods -n epfl-eso-addlidar-prod`
- Verify the namespace name is correct
- Ensure you have proper RBAC permissions

### Permission denied errors

- Check if you have read access to the production namespace
- Verify the pod contains the database file at the expected path

### Empty or corrupted snapshots

- Check if the source database file exists in the pod
- Verify the pod has the database at `/app/data/database.db`
- Try downloading from a different pod

## Examples

### Daily Development Workflow

```bash
# Start of day - get latest production data
make snapshot-download

# Work with fresh production data
make run

# Before major changes - backup current state
make snapshot-backup

# Test with different data
make snapshot-switch-to SNAPSHOT=./snapshots/snapshot_prod_2025_06_15_090000.db
```

### Testing Different Scenarios

```bash
# Download multiple snapshots from different times
./snapshot.sh download

# List available snapshots
make snapshot-list

# Test with older data
make snapshot-switch-to SNAPSHOT=./snapshots/snapshot_prod_2025_06_12_100000.db

# Return to latest
make snapshot-switch-to SNAPSHOT=./snapshots/snapshot_prod_2025_06_16_120000.db
```

## Security Notes

- Snapshots may contain production data - treat them securely
- Don't commit snapshot files to version control
- The `snapshots/` directory is gitignored by default
- Consider encrypting snapshots if they contain sensitive data

## Contributing

To improve the snapshot management system:

1. Edit `src/utils/snapshot_manager.py` for core functionality
2. Update `snapshot.sh` for convenience scripts
3. Add new Makefile targets for common workflows
4. Update this README with new features
