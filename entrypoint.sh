#!/bin/bash
set -e

# Expected environment variables:
#   INPUT_FILE:   The file to be converted (e.g., /data/input.las)
#   OUTPUT_DIR:   The directory where the .octree will be stored (e.g., /data/octree_output)
#   S3_BUCKET:    The S3 destination bucket (e.g., s3://your-bucket/path/)
#
#   ACCESS_KEY:   Your S3 access key.
#   PRIVATE_KEY:  Your S3 secret key.
#
#   EXTRA_ARGS:   (Optional) Additional arguments for PotreeConverter

# Check for required conversion variables
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

# Check for S3 credentials
if [ -z "$ACCESS_KEY" ] || [ -z "$PRIVATE_KEY" ]; then
  echo "ERROR: Both ACCESS_KEY and PRIVATE_KEY must be set"
  exit 1
fi

# Create a temporary s3cfg file based on environment variables.
# Adjust host_base/host_bucket if you are using a non-AWS S3 service.
S3CFG_FILE="/tmp/s3cfg"
cat <<EOF > "$S3CFG_FILE"
[default]
access_key = ${ACCESS_KEY}
secret_key = ${PRIVATE_KEY}
host_base = s3.epfl.ch
host_bucket = s3.epfl.ch/%(bucket)
use_https = True
EOF

echo "Temporary s3cfg file created at $S3CFG_FILE"

echo "Starting PotreeConverter conversion..."
LD_PRELOAD=/app/liblaszip.so /app/PotreeConverter "$INPUT_FILE" -o "$OUTPUT_DIR" $EXTRA_ARGS

echo "Conversion completed. Uploading output to S3..."
s3cmd --config="$S3CFG_FILE" put --guess-mime-type --acl-public --recursive -v --progress "$OUTPUT_DIR/" "$S3_BUCKET"

echo "S3 upload complete."
