#!/bin/bash

# Build and push scanner image with special tag for RCP-HAAS deployment

set -e

# Configuration
REGISTRY="ghcr.io"
ORG="epfl-enac"
PROJECT="epfl-eso/addlidar"
IMAGE_NAME="scanner"
TAG="${1:-rcp-haas-$(date +%Y%m%d-%H%M%S)}"

FULL_IMAGE_NAME="${REGISTRY}/${ORG}/${PROJECT}/${IMAGE_NAME}:${TAG}"

echo "Building scanner image: ${FULL_IMAGE_NAME}"

# Build the image
docker buildx build --platform linux/amd64 -t "${FULL_IMAGE_NAME}" .

echo "Image built successfully: ${FULL_IMAGE_NAME}"

# Check if we should push
read -p "Push image to registry? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Pushing image to registry..."
    docker push "${FULL_IMAGE_NAME}"
    echo "Image pushed successfully!"
    echo "Image available at: ${FULL_IMAGE_NAME}"
else
    echo "Image not pushed. To push manually run:"
    echo "docker push ${FULL_IMAGE_NAME}"
fi
