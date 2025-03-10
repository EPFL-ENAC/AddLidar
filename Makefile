# Makefile

# Download .zip linux x64 from https://github.com/potree/PotreeConverter/releases/tag/2.1.1
# https://github.com/potree/PotreeConverter/releases/download/2.1.1/PotreeConverter_2.1.1_x64_linux.zip

# Variables
IMAGE_NAME = ghcr.io/epfl-enac/potree_converter:2.1.1
CONTAINER_NAME = potree_converter_container

install:
	@echo "Downloading PotreeConverter..."
	./download-release.sh
	@echo "PotreeConverter downloaded successfully"

build: install check
	@echo "Building Docker image..."
	docker buildx build --platform linux/amd64 -t $(IMAGE_NAME) --push .

# Run the Docker container
run:
	@echo "Running Docker container..."
	docker run --platform linux/amd64 --name $(CONTAINER_NAME) -d $(IMAGE_NAME)

# Run with input/output volume mounts
convert:
	@echo "Enter the path to your point cloud file: "
	@read input_file; \
	echo "Enter the output directory path: "; \
	read output_dir; \
	docker run --platform linux/amd64 --rm \
		-v "$${input_file}:/input/pointcloud.las" \
		-v "$${output_dir}:/output" \
		$(IMAGE_NAME) \
		-i /input/pointcloud.las -o /output

# Stop the Docker container
stop:
	docker stop $(CONTAINER_NAME)

# Remove the Docker container
clean:
	rm -rf PotreeConverter
	docker rm $(CONTAINER_NAME)

# Remove the Docker image
clean-image:
	docker rmi $(IMAGE_NAME)

# Check if Dockerfile exists
check:
	@if [ ! -f "Dockerfile" ]; then \
		echo "ERROR: Dockerfile not found in the current directory"; \
		exit 1; \
	fi


.PHONY: build run stop clean clean-image