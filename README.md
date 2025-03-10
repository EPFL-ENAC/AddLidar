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

### Build the Docker image

```bash
docker buildx build --platform linux/amd64 -t ghcr.io/epfl-enac/potree_converter:2.1.1 --push .
```

### Run with volume mounts

```bash
# Using make
make convert

# Manual docker run
docker run --platform linux/amd64 --rm \
    -v "/path/to/input/file.las:/input/pointcloud.las" \
    -v "/path/to/output/directory:/output" \
    ghcr.io/epfl-enac/potree_converter:2.1.1 \
    -i /input/pointcloud.las -o /output
```

## S3 Upload Feature

This container includes functionality to automatically upload converted point clouds to an S3 bucket.

### Environment Variables

When using the entrypoint.sh script, set the following environment variables:

- `INPUT_FILE`: Path to the input point cloud file (e.g., /data/input.las)
- `OUTPUT_DIR`: Directory where the output will be stored (e.g., /data/output)
- `S3_BUCKET`: S3 bucket destination (e.g., s3://your-bucket/path/)
- `EXTRA_ARGS`: (Optional) Additional arguments for PotreeConverter

### Example with S3 upload

```bash
docker run --platform linux/amd64 --rm \
    -v "/path/to/input/file.las:/data/input.las" \
    -v "/path/to/output/directory:/data/output" \
    -e INPUT_FILE=/data/input.las \
    -e OUTPUT_DIR=/data/output \
    -e S3_BUCKET=s3://your-bucket/path/ \
    -e EXTRA_ARGS="--generate-page" \
    --entrypoint /app/entrypoint.sh \
    ghcr.io/epfl-enac/potree_converter:2.1.1
```

## Common PotreeConverter Arguments

- `-h, --help`: Display help information
- `-o, --outdir`: Output directory
- `-g, --generate-page`: Generate a ready-to-use web page with the viewer
- `--material`: RGB, ELEVATION, INTENSITY, INTENSITY_GRADIENT, CLASSIFICATION, RETURN_NUMBER, SOURCE, LEVEL_OF_DETAIL
- `--output-format`: BINARY, LAS, LAZ
- `--scale`: Scale factor for precision (default: 0.001)

For a complete list of arguments, run:

```bash
docker run --rm ghcr.io/epfl-enac/potree_converter:2.1.1 --help
```

## License

PotreeConverter is released under the [MIT License](https://github.com/potree/PotreeConverter/blob/master/LICENSE).