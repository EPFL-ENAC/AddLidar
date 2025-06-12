# LiDAR ZIP Archive Tool

This tool creates compressed archives for LiDAR data folders as part of the AddLidar project.

## Overview

The LiDAR ZIP Archive Tool is a containerized utility that helps package LiDAR datasets for easier distribution. It's designed to work with the AddLidar web-based system for storing, processing, and visualizing LiDAR datasets collected from airborne missions.

## Prerequisites

- Docker installed on your system
- Access to LiDAR data folders you want to compress
- GitHub Container Registry (ghcr.io) credentials (if pushing the image)

## Integration with AddLidar

This tool is part of the AddLidar system, which is deployed on a Kubernetes cluster. It's designed to be run as a Kubernetes job for processing LiDAR datasets as part of the overall workflow.

## Updating the Docker Image

WARNING : enack8s-app-config/epfl-eso/addlidar/overlays/prod/kustomization.yaml needs to manually updated with the new image tag after each build (image tag is not automatically updated by the CD).
