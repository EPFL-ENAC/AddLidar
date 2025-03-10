#!/bin/bash
set -e

# Expected environment variables:
#   INPUT_FILE:   The file to be converted (e.g., /data/input.las)
#   OUTPUT_DIR:   The directory where the .octree will be stored (e.g., /data/octree_output)
#   S3_BUCKET:    The S3 destination bucket (e.g., s3://your-bucket/path/)
#   EXTRA_ARGS:   (Optional) Additional arguments for PotreeConverter

# Check for required variables
if [ -z "$INPUT_FILE" ]; then
  echo "ERROR: INPUT_FILE is not set"
  exit 1
fi

if [ -z "$OUTPUT_DIR" ]; then
  echo "ERROR: OUTPUT_DIR is not set"
  exit 1
fi

if [ -z "$S3_BUCKET" ]; then
  echo "ERROR: S3_BUCKET is not set"
  exit 1
fi

echo "Starting PotreeConverter conversion..."
LD_PRELOAD=/app/liblaszip.so /app/PotreeConverter "$INPUT_FILE" -o "$OUTPUT_DIR" $EXTRA_ARGS

echo "Conversion completed. Uploading output to S3..."
s3cmd put --guess-mime-type --acl-public --recursive -v "$OUTPUT_DIR/" "$S3_BUCKET"

echo "S3 upload complete."
