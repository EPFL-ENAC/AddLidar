# LiDAR Archive Scanner

## Overview

The LiDAR Archive Scanner is a Python-based application designed to scan directories containing LiDAR data and queue jobs for creating compressed archives. It utilizes Kubernetes for job management and SQLite for state tracking.

# Beware

1. Namespace is hard-coded in the \*.template.yaml files: it's on purpose, we only want to run them on one namespace
