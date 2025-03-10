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
docker build -f Dockerfile --platform linux/amd64 -t ghcr.io/epfl-enac/potree_converter:debian-2.1.1 ./PotreeConverter
```

## S3 Upload Feature

This container includes functionality to automatically upload converted point clouds to an S3 bucket.

### Environment Variables

When using the entrypoint.sh script, set the following environment variables:

- `INPUT_FILE`: Path to the input point cloud file (e.g., /data/input.las)
- `OUTPUT_DIR`: Directory where the output will be stored (e.g., /data/output)
- `S3_BUCKET`: S3 bucket destination (e.g., s3://your-bucket/path/)
- `ACCESS_KEY`: S3 access key
- `PRIVATE_KEY`: S3 private key

- `EXTRA_ARGS`: (Optional) Additional arguments for PotreeConverter

### Example with S3 upload

```bash
docker run --platform linux/amd64  --rm \
  -v /path/to/data:/data \
  -v /path/to/output/directory:/output \
  -e INPUT_FILE="/data/LiDAR/0002_Val_dArpette/02_RAW_LAZ/ARPETTE_LV95_HELL_1560II_CH1_211020_082047.laz" \
  -e OUTPUT_DIR="/output" \
  -e S3_BUCKET="s3://XXXXXXXXXXXX/AddLidar/ARPETTE_LV95_HELL_1560II_CH1_211020_082047/" \
  -e ACCESS_KEY="XXXXXXXXXXXX" \
  -e PRIVATE_KEY="XXXXXXXXXXXX" \
  ghcr.io/epfl-enac/potree_converter:debian-2.1.1
```

## Common PotreeConverter Arguments

- `-h, --help`: Display help information
- `-o, --outdir`: Output directory
- `-g, --generate-page`: Generate a ready-to-use web page with the viewer
- `--material`: RGB, ELEVATION, INTENSITY, INTENSITY_GRADIENT, CLASSIFICATION, RETURN_NUMBER, SOURCE, LEVEL_OF_DETAIL
- `--output-format`: BINARY, LAS, LAZ
- `--scale`: Scale factor for precision (default: 0.001)

## License

PotreeConverter is released under the [MIT License](https://github.com/potree/PotreeConverter/blob/master/LICENSE).