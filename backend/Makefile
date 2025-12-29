install:
	$(MAKE) -C lidar-api install

dev:
	@echo "Starting backend in development mode..."
	$(MAKE) -C lidar-api run

run:
	$(MAKE) -C lidar-api run

build:
	@echo "Building backend..."
	@if [ -f lidar-api/Makefile ] && grep -q "^build:" lidar-api/Makefile; then \
		$(MAKE) -C lidar-api build; \
	else \
		echo "No build target found in lidar-api, skipping..."; \
	fi

test:
	$(MAKE) -C lidar-api test

format:
	$(MAKE) -C lidar-api format

lint:
	$(MAKE) -C lidar-api lint
	
# Lefthook commands
install-lefthook:
	@echo "Installing lefthook..."
	@if command -v npm >/dev/null 2>&1; then \
		npm install -g lefthook; \
	else \
		echo "Error: npm not found. Please install Node.js and npm."; \
		exit 1; \
	fi
	@echo "Lefthook installed successfully!"

init-lefthook:
	@echo "Initializing lefthook..."
	@if command -v lefthook >/dev/null 2>&1; then \
		lefthook install; \
	else \
		echo "Error: lefthook not found. Please run 'make install-lefthook' first."; \
		exit 1; \
	fi
	@echo "Git hooks installed successfully!"

setup-hooks: install-lefthook init-lefthook