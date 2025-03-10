#!/bin/bash

# GitHub API URL for releases
REPO="potree/PotreeConverter"
API_URL="https://api.github.com/repos/$REPO/releases"

# Fetch the latest releases (limit to 5) and extract tag names
RELEASES=$(curl -s "$API_URL" | jq -r '.[0:5] | .[].tag_name')

# Convert releases into an array
RELEASES_ARRAY=()
while IFS= read -r line; do
    RELEASES_ARRAY+=("$line")
done <<< "$RELEASES"

# Display the options
echo "Select a release:"
for i in "${!RELEASES_ARRAY[@]}"; do
    echo "$((i+1))) ${RELEASES_ARRAY[i]}"
done

# Get user selection
read -p "Enter the number of the release: " CHOICE
if [[ "$CHOICE" =~ ^[1-5]$ ]]; then
    SELECTED_RELEASE="${RELEASES_ARRAY[CHOICE-1]}"
    echo "You selected: $SELECTED_RELEASE"
    DOWNLOAD_RELEASE="https://github.com/$REPO/releases/tag/$SELECTED_RELEASE"
    DOWNLOAD_URL="https://github.com/$REPO/releases/download/$SELECTED_RELEASE/PotreeConverter_${SELECTED_RELEASE}_x64_linux.zip"
    echo "URL: $DOWNLOAD_URL"
    wget -v $DOWNLOAD_URL
    unzip PotreeConverter_${SELECTED_RELEASE}_x64_linux.zip
    rm PotreeConverter_${SELECTED_RELEASE}_x64_linux.zip
	mv PotreeConverter_linux_x64 PotreeConverter
    rm -rf PotreeConverter_linux_x64
	rm -rf PotreeConverter/resources
	chmod +x PotreeConverter/PotreeConverter
    cp Dockerfile PotreeConverter/
    cp entrypoint.sh PotreeConverter/
else
    echo "Invalid selection."
fi
