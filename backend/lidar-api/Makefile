# Define Python version (optional)
PYTHON_VERSION = 3.11.5

# Sync dependencies
sync:
	@echo "Syncing dependencies"
	uv sync

# Run both public and internal servers
run:
	@echo "Starting both public (port 8000) and internal (port 8001) servers"
	uv run python -m src.main

# Run only public server (for development/testing)
run-public:
	@echo "Starting public server only on port 8000"
	uv run uvicorn src.main:public_app --reload --host 0.0.0.0 --port 8000 --log-level debug --access-log --use-colors

# Run only internal server (for development/testing)
run-internal:
	@echo "Starting internal server only on port 8001"
	uv run uvicorn src.main:internal_app --reload --host 0.0.0.0 --port 8001 --log-level debug --access-log --use-colors

# Legacy run command for backwards compatibility
run-legacy:
	@echo "Starting legacy single server on port 8000"
	uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug --access-log --use-colors



run-worker:
	REDIS_HOST=localhost uv run celery -A src.celery_worker worker --loglevel=info



docker-build:
	@echo "Building docker image"
	docker build -t lidar-api .

docker-run: docker-build
	@echo "Running docker image"
	@echo "Public API: http://localhost:8000"
	@echo "Internal API: http://localhost:8001"
	docker run -p 8000:8000 -p 8001:8001 lidar-api:latest



format:
	black src

lint:
	flake8 src --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src --count --exit-zero --max-complexity=15 --max-line-length=127 --statistics

test:
	uv run pytest

scout:
	docker scout cves local://lidar-api:latest

# Database snapshot management
snapshot-list:
	@echo "Listing local database snapshots..."
	./snapshot.sh list

snapshot-download:
	@echo "Downloading latest snapshot from production..."
	./snapshot.sh download

snapshot-backup:
	@echo "Creating backup of current database..."
	./snapshot.sh backup

snapshot-switch:
	@echo "Available snapshots:"
	@./snapshot.sh list
	@echo ""
	@echo "To switch to a snapshot, use: make snapshot-switch-to SNAPSHOT=<path>"
	@echo "Example: make snapshot-switch-to SNAPSHOT=./snapshots/snapshot_prod_2025_06_16_120000.db"

snapshot-switch-to:
	@if [ -z "$(SNAPSHOT)" ]; then \
		echo "Error: SNAPSHOT variable is required"; \
		echo "Usage: make snapshot-switch-to SNAPSHOT=<path>"; \
		exit 1; \
	fi
	@echo "Switching to snapshot: $(SNAPSHOT)"
	./snapshot.sh switch "$(SNAPSHOT)"

snapshot-help:
	@echo "Database Snapshot Management Commands:"
	@echo "  make snapshot-list        - List all local snapshots"
	@echo "  make snapshot-download     - Download latest from production"
	@echo "  make snapshot-backup       - Backup current database"
	@echo "  make snapshot-switch       - Show available snapshots and instructions"
	@echo "  make snapshot-switch-to SNAPSHOT=<path> - Switch to specific snapshot"
	@echo ""
	@echo "Examples:"
	@echo "  make snapshot-download"
	@echo "  make snapshot-list"
	@echo "  make snapshot-switch-to SNAPSHOT=./snapshots/snapshot_prod_2025_06_16_120000.db"

# Database deployment to Kubernetes environments
db-push-dev:
	@echo "Finding backend pod in dev environment..."
	$(eval DEV_POD := $(shell kubectl get pods -n epfl-eso-addlidar-dev | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -z "$(DEV_POD)" ]; then \
		echo "Error: No running backend pod found in epfl-eso-addlidar-dev namespace"; \
		exit 1; \
	fi
	@echo "Pushing database to dev pod: $(DEV_POD)"
	kubectl cp -n epfl-eso-addlidar-dev ./data/database.db $(DEV_POD):/db-path/lidar-archive.db
	@echo "Database successfully pushed to dev environment"

db-push-prod:
	@echo "Finding backend pod in prod environment..."
	$(eval PROD_POD := $(shell kubectl get pods -n epfl-eso-addlidar-prod | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -z "$(PROD_POD)" ]; then \
		echo "Error: No running backend pod found in epfl-eso-addlidar-prod namespace"; \
		exit 1; \
	fi
	@echo "Pushing database to prod pod: $(PROD_POD)"
	kubectl cp -n epfl-eso-addlidar-prod ./data/database.db $(PROD_POD):/db-path/lidar-archive.db
	@echo "Database successfully pushed to prod environment"

db-push-rcp-haas:
	@echo "Finding backend pod in rcp-haas environment..."
	$(eval RCP_POD := $(shell kubectl get pods -n epfl-eso-addlidar-rcp-haas | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -z "$(RCP_POD)" ]; then \
		echo "Error: No running backend pod found in epfl-eso-addlidar-rcp-haas namespace"; \
		exit 1; \
	fi
	@echo "Pushing database to rcp-haas pod: $(RCP_POD)"
	kubectl cp -n epfl-eso-addlidar-rcp-haas ./data/database.db $(RCP_POD):/db-path/lidar-archive.db
	@echo "Database successfully pushed to rcp-haas environment"

db-push-all:
	@echo "Pushing database to all environments..."
	@$(MAKE) db-push-dev
	@$(MAKE) db-push-prod  
	@$(MAKE) db-push-rcp-haas
	@echo "Database successfully pushed to all environments"

db-pull-dev:
	@echo "Finding backend pod in dev environment..."
	$(eval DEV_POD := $(shell kubectl get pods -n epfl-eso-addlidar-dev | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -z "$(DEV_POD)" ]; then \
		echo "Error: No running backend pod found in epfl-eso-addlidar-dev namespace"; \
		exit 1; \
	fi
	@echo "Pulling database from dev pod: $(DEV_POD)"
	kubectl cp -n epfl-eso-addlidar-dev $(DEV_POD):/db-path/lidar-archive.db ./data/database-from-dev.db
	@echo "Database pulled from dev environment to ./data/database-from-dev.db"

db-pull-prod:
	@echo "Finding backend pod in prod environment..."
	$(eval PROD_POD := $(shell kubectl get pods -n epfl-eso-addlidar-prod | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -z "$(PROD_POD)" ]; then \
		echo "Error: No running backend pod found in epfl-eso-addlidar-prod namespace"; \
		exit 1; \
	fi
	@echo "Pulling database from prod pod: $(PROD_POD)"
	kubectl cp -n epfl-eso-addlidar-prod $(PROD_POD):/db-path/lidar-archive.db ./data/database-from-prod.db
	@echo "Database pulled from prod environment to ./data/database-from-prod.db"

db-pull-rcp-haas:
	@echo "Finding backend pod in rcp-haas environment..."
	$(eval RCP_POD := $(shell kubectl get pods -n epfl-eso-addlidar-rcp-haas | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -z "$(RCP_POD)" ]; then \
		echo "Error: No running backend pod found in epfl-eso-addlidar-rcp-haas namespace"; \
		exit 1; \
	fi
	@echo "Pulling database from rcp-haas pod: $(RCP_POD)"
	kubectl cp -n epfl-eso-addlidar-rcp-haas $(RCP_POD):/db-path/lidar-archive.db ./data/database-from-rcp-haas.db
	@echo "Database pulled from rcp-haas environment to ./data/database-from-rcp-haas.db"

db-status:
	@echo "Checking database status in all environments..."
	@echo ""
	@echo "=== DEV Environment ==="
	$(eval DEV_POD := $(shell kubectl get pods -n epfl-eso-addlidar-dev | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -n "$(DEV_POD)" ]; then \
		echo "Pod: $(DEV_POD)"; \
		kubectl exec -n epfl-eso-addlidar-dev $(DEV_POD) -- ls -la /db-path/ 2>/dev/null || echo "Database path not accessible"; \
	else \
		echo "No running backend pod found"; \
	fi
	@echo ""
	@echo "=== PROD Environment ==="
	$(eval PROD_POD := $(shell kubectl get pods -n epfl-eso-addlidar-prod | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -n "$(PROD_POD)" ]; then \
		echo "Pod: $(PROD_POD)"; \
		kubectl exec -n epfl-eso-addlidar-prod $(PROD_POD) -- ls -la /db-path/ 2>/dev/null || echo "Database path not accessible"; \
	else \
		echo "No running backend pod found"; \
	fi
	@echo ""
	@echo "=== RCP-HAAS Environment ==="
	$(eval RCP_POD := $(shell kubectl get pods -n epfl-eso-addlidar-rcp-haas | grep backend | grep Running | awk '{print $$1}' | head -1))
	@if [ -n "$(RCP_POD)" ]; then \
		echo "Pod: $(RCP_POD)"; \
		kubectl exec -n epfl-eso-addlidar-rcp-haas $(RCP_POD) -- ls -la /db-path/ 2>/dev/null || echo "Database path not accessible"; \
	else \
		echo "No running backend pod found"; \
	fi
	@echo ""
	@echo "=== LOCAL Database ==="
	@ls -la ./data/database.db 2>/dev/null || echo "Local database not found"

db-help:
	@echo "Database Kubernetes Deployment Commands:"
	@echo "  make db-push-dev          - Push local database to dev environment"
	@echo "  make db-push-prod         - Push local database to prod environment"
	@echo "  make db-push-rcp-haas     - Push local database to rcp-haas environment"
	@echo "  make db-push-all          - Push local database to all environments"
	@echo ""
	@echo "  make db-pull-dev          - Pull database from dev environment"
	@echo "  make db-pull-prod         - Pull database from prod environment"
	@echo "  make db-pull-rcp-haas     - Pull database from rcp-haas environment"
	@echo ""
	@echo "  make db-status            - Show database status in all environments"
	@echo "  make db-help              - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make db-push-rcp-haas     # Push to rcp-haas only"
	@echo "  make db-push-all          # Push to all environments"
	@echo "  make db-status            # Check all environments"