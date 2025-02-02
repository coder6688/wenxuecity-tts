#!/bin/bash

# Parse command-line arguments with defaults
VERSION=${1:-"v0.0.3"}                  # First argument: version (default: v0.0.3)
BUILD_DATE=${2:-$(date +"%Y%m%d")}      # Second argument: build date (default: current date)

# Validate date format
if ! [[ $BUILD_DATE =~ ^[0-9]{8}$ ]]; then
    echo "Error: Invalid date format. Use YYYYMMDD (e.g., 20250202)"
    exit 1
fi

# Create GitHub release
gh release create ${VERSION} \
  --title "Version ${VERSION}" \
  --notes "Release ${VERSION} (${BUILD_DATE})" \
  "dist/WenxuecityTTS_${BUILD_DATE}.dmg" \
  "dist/WenxuecityTTS_${BUILD_DATE}.exe"

# Usage examples:
# ./gh_release.sh                  # Uses v0.0.3 and current date
# ./gh_release.sh v0.1.0           # Uses v0.1.0 and current date
# ./gh_release.sh v0.1.0 20250202 # Uses specified version and date