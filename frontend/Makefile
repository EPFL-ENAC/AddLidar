.PHONY: install dev run build build-potree clean lint format help

install:
	@echo "Installing frontend dependencies..."
	npm install

dev:
	@echo "Starting frontend in development mode..."
	npm run dev

dev-local:
	@echo "Starting frontend with local backend proxy..."
	npm run dev:local

dev-prod:
	@echo "Starting frontend with production backend proxy..."
	npm run dev:prod

run:
	@echo "Starting frontend with Docker Compose..."
	docker compose build --parallel --pull
	docker compose up -d --remove-orphans --force-recreate

build:
	@echo "Building frontend for production..."
	npm run build

build-potree:
	@echo "Building Potree library..."
	npm run build-potree

clean:
	@echo "Cleaning frontend build artifacts and dependencies..."
	rm -rf node_modules dist build vueSrc/public/build vueSrc/public/libs

help:
	@echo "Frontend Makefile - Available Commands:"
	@echo "======================================="
	@echo ""
	@echo "Development:"
	@echo "  dev        - Start Vite dev server (default proxies)"
	@echo "  dev-local  - Start dev server with local backend"
	@echo "  dev-prod   - Start dev server with production backend"
	@echo "  install    - Install npm dependencies"
	@echo ""
	@echo "Production:"
	@echo "  build      - Build frontend for production"
	@echo "  build-potree - Build Potree library only"
	@echo "  run        - Run with Docker Compose"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean      - Remove build artifacts and dependencies"
	@echo "  help       - Show this help message"
