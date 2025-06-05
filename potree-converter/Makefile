# Makefile for PotreeConverter with metacloud support

# Variables
IMAGE_NAME = ghcr.io/epfl-enac/potree_converter:latest
CONTAINER_NAME = potree_converter_container

build: install check
	@echo "Building Docker image..."
	docker buildx build -f Dockerfile --platform linux/amd64 -t $(IMAGE_NAME) .

push-image:
	@echo "Pushing Docker image to GitHub Container Registry..."
	docker push $(IMAGE_NAME)
	@echo "Docker image pushed successfully"

# Run with metacloud file
convert-metacloud:
	@echo "Enter the path to your .metacloud file: "
	@read metacloud_file; \
	echo "Enter the output directory path: "; \
	read output_dir; \
	metacloud_dir=$$(dirname "$${metacloud_file}"); \
	metacloud_filename=$$(basename "$${metacloud_file}"); \
	echo "Running docker with metacloud file..."; \
	docker run --platform linux/amd64 --rm \
		-v "$${metacloud_dir}:/input" \
		-v "$${output_dir}:/output" \
		-e INPUT_FILE="/input/$${metacloud_filename}" \
		-e OUTPUT_DIR="/output" \
		-e EXTRA_ARGS="" \
		$(IMAGE_NAME)

# Clean up
clean:
	rm -rf PotreeConverter
	-docker rm $(CONTAINER_NAME) 2>/dev/null || true

# Clean image
clean-image:
	-docker rmi $(IMAGE_NAME) 2>/dev/null || true

# Check if Dockerfile exists
check:
	@if [ ! -f "Dockerfile" ]; then \
		echo "ERROR: Dockerfile not found in the current directory"; \
		exit 1; \
	fi

.PHONY: install build convert-metacloud clean clean-image check