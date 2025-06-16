#!/bin/bash
# Quick snapshot management script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SNAPSHOT_MANAGER="$SCRIPT_DIR/src/utils/snapshot_manager.py"

# Make the Python script executable
chmod +x "$SNAPSHOT_MANAGER"

# Function to show usage
show_usage() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Commands:"
    echo "  list                 - List all local database snapshots"
    echo "  download             - Download latest snapshot from production"
    echo "  download-pod <name>  - Download from specific pod"
    echo "  switch <path>        - Switch to specific snapshot"
    echo "  backup               - Backup current database"
    echo "  help                 - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 list                                    # List local snapshots"
    echo "  $0 download                                # Auto-download from production"
    echo "  $0 switch ./snapshots/snapshot_prod_*.db   # Switch to specific snapshot"
    echo "  $0 backup                                  # Backup current database"
}

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "Error: 'uv' is not installed or not in PATH"
    echo "Please install uv first: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Parse command
case "$1" in
    "list")
        echo "Listing local database snapshots..."
        uv run python "$SNAPSHOT_MANAGER" list
        ;;
    "download")
        echo "Downloading latest snapshot from production..."
        uv run python "$SNAPSHOT_MANAGER" download --auto
        ;;
    "download-pod")
        if [ -z "$2" ]; then
            echo "Error: Pod name required"
            echo "Usage: $0 download-pod <pod_name>"
            exit 1
        fi
        echo "Downloading snapshot from pod: $2"
        uv run python "$SNAPSHOT_MANAGER" download --pod "$2"
        ;;
    "switch")
        if [ -z "$2" ]; then
            echo "Error: Snapshot path required"
            echo "Usage: $0 switch <snapshot_path>"
            exit 1
        fi
        echo "Switching to snapshot: $2"
        uv run python "$SNAPSHOT_MANAGER" switch "$2"
        ;;
    "backup")
        echo "Creating backup of current database..."
        uv run python "$SNAPSHOT_MANAGER" backup
        ;;
    "help"|"-h"|"--help")
        show_usage
        ;;
    *)
        if [ -z "$1" ]; then
            show_usage
        else
            echo "Error: Unknown command '$1'"
            echo ""
            show_usage
            exit 1
        fi
        ;;
esac
