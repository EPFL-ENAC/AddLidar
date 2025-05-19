#!/bin/bash
set -e

# Expected environment variables:
#   INPUT_FILE:   The .metacloud file listing point cloud files to process
#   OUTPUT_DIR:   The directory where the converted files will be stored
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

# Ensure INPUT_FILE is a .metacloud file
if [[ ! "$INPUT_FILE" == *.metacloud ]]; then
  echo "ERROR: INPUT_FILE must be a .metacloud file"
  exit 1
fi

echo "DEBUG: Script starting"
echo "DEBUG: INPUT_FILE=$INPUT_FILE"
echo "DEBUG: OUTPUT_DIR=$OUTPUT_DIR"
echo "DEBUG: EXTRA_ARGS=$EXTRA_ARGS"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Parse the .metacloud file and collect all point cloud files
PARSING_POINTS_FILES=false
FILE_COUNT=0
POINT_CLOUD_FILES=()

while IFS= read -r line; do
  # Skip comments and empty lines
  echo "DEBUG: Processing line: $line"
  [[ "$line" =~ ^#.*$ || -z "$line" ]] && continue
  
  # Check section markers
  if [[ "$line" == "POINTS_FILES" ]]; then
    PARSING_POINTS_FILES=true
    continue
  elif [[ "$line" == "METACLOUD_ATTRIBUTES" ]]; then
    PARSING_POINTS_FILES=false
    continue
  fi
  
  # Process file paths in POINTS_FILES section
  if [ "$PARSING_POINTS_FILES" = true ]; then
    # Remove leading ./ from the line if present
    clean_path="${line#./}"
    
    echo "DEBUG: Cleaned path: $clean_path"
    # Since we're mounting the directory containing the .metacloud file to /input,
    # we need to append the relative path to /input
    point_cloud_file="/input/${clean_path}"
    echo "DEBUG: Full path to point cloud file: $point_cloud_file"
    if [ ! -f "$point_cloud_file" ]; then
      echo "WARNING: File not found: $point_cloud_file"
    fi
    
    # Add to the array of files
    POINT_CLOUD_FILES+=("$point_cloud_file")
    echo "DEBUG: Added file to array: $point_cloud_file"
    FILE_COUNT=$(($FILE_COUNT + 1))
    echo "DEBUG: File count: $FILE_COUNT"
    echo "Found file $FILE_COUNT: $point_cloud_file"
  fi
done < "$INPUT_FILE"

echo "DEBUG: Found files: ${POINT_CLOUD_FILES[@]}"


# Check if we found any files
if [ ${#POINT_CLOUD_FILES[@]} -eq 0 ]; then
  echo "ERROR: No point cloud files found in the metacloud file."
  exit 1
fi

echo "Found $FILE_COUNT files to process."

echo "DEBUG: About to run: /app/PotreeConverter ${POINT_CLOUD_FILES[@]} -o $OUTPUT_DIR $EXTRA_ARGS"

# Convert all files in a single PotreeConverter command
echo "Starting PotreeConverter conversion with all files..."
LD_PRELOAD=/app/liblaszip.so /app/PotreeConverter "${POINT_CLOUD_FILES[@]}" -o "$OUTPUT_DIR" $EXTRA_ARGS
echo "Conversion completed."

echo "Processing complete. Processed $FILE_COUNT files from .metacloud."
echo "Results stored in: $OUTPUT_DIR"