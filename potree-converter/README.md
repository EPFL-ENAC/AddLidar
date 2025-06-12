# PotreeConverter Docker Container

This repository contains a Docker implementation of [PotreeConverter](https://github.com/potree/PotreeConverter), a tool for converting point cloud data (LAS/LAZ/PTX/PLY...) to the Potree format for web-based rendering.

## Installation

You can install PotreeConverter using the provided Makefile:

```bash
# Download and install PotreeConverter
make install

# Build the Docker image
make build
```

## Docker Usage

### Build the Docker image locally

```bash
make install
docker build -f Dockerfile --platform linux/amd64 -t ghcr.io/epfl-enac/potree_converter:debian-2.1.1 .
```

## Updating the Docker Image

WARNING : enack8s-app-config/epfl-eso/addlidar/overlays/prod/kustomization.yaml needs to manually updated with the new image tag after each build (image tag is not automatically updated by the CD).

## Using .metacloud Files

This container supports processing point cloud files listed in a `.metacloud` file. A `.metacloud` file is a text file that contains paths to multiple point cloud files to be processed together.

### .metacloud File Format

```
POINTS_FILES
./path/to/file1.las
./path/to/file2.las
./path/to/file3.las

METACLOUD_ATTRIBUTES
creator "Your Name"
description "Description of your point cloud dataset"
```

The paths in the `.metacloud` file should be relative to the directory containing the `.metacloud` file. When mounting directories to the Docker container, ensure the directory structure matches the paths in your `.metacloud` file.

For example, if your `.metacloud` file references `./01_Lidar_Processed_las/file.las`, you should mount the parent directory of `01_Lidar_Processed_las` to `/input` in the container.

### Environment Variables

When using the entrypoint.sh script, set the following environment variables:

- `INPUT_FILE`: Path to the input `.metacloud` file (e.g., /input/point_cloud.metacloud)
- `OUTPUT_DIR`: Directory where the output will be stored (e.g., /output)
- `EXTRA_ARGS`: (Optional) Additional arguments for PotreeConverter

### Example with .metacloud file

```bash
docker run --platform linux/amd64 --rm \
  -v "/path/to/input/directory:/input" \
  -v "/path/to/output/directory:/output" \
  -e INPUT_FILE="/input/point_cloud_las.metacloud" \
  -e OUTPUT_DIR="/output" \
  ghcr.io/epfl-enac/potree_converter:debian-2.1.1
```

### Working Example

```bash
docker run --platform linux/amd64 --rm \
  -v "/home/pierre/dev/PotreeConverterMakefile/input:/input" \
  -v "/home/pierre/dev/PotreeConverterMakefile/output:/output" \
  -e INPUT_FILE="/input/point_cloud_las.metacloud" \
  -e OUTPUT_DIR="/output" \
  ghcr.io/epfl-enac/potree_converter:debian-2.1.1
```

### Using the Makefile for Convenience

You can use the `convert-metacloud` target in the Makefile for an interactive prompt:

```bash
make convert-metacloud
```

This will prompt you for:

1. The path to your `.metacloud` file
2. The output directory path

And then run the Docker container with the appropriate parameters.

## Common PotreeConverter Arguments

- `-h, --help`: Display help information
- `-o, --outdir`: Output directory
- `-g, --generate-page`: Generate a ready-to-use web page with the viewer
- `--material`: RGB, ELEVATION, INTENSITY, INTENSITY_GRADIENT, CLASSIFICATION, RETURN_NUMBER, SOURCE, LEVEL_OF_DETAIL
- `--output-format`: BINARY, LAS, LAZ
- `--scale`: Scale factor for precision (default: 0.001)

## License

PotreeConverter is released under the [MIT License](https://github.com/potree/PotreeConverter/blob/master/LICENSE).
