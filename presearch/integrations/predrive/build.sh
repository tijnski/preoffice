#!/bin/bash
# Build PreDrive extension package (.oxt)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXTENSION_NAME="predrive"
VERSION="1.0.0"
OUTPUT_DIR="${SCRIPT_DIR}/dist"
OUTPUT_FILE="${OUTPUT_DIR}/${EXTENSION_NAME}-${VERSION}.oxt"

echo "Building PreDrive Extension v${VERSION}..."

# Create output directory
mkdir -p "${OUTPUT_DIR}"

# Remove old package if exists
rm -f "${OUTPUT_FILE}"

# Create temporary build directory
BUILD_DIR=$(mktemp -d)
trap "rm -rf ${BUILD_DIR}" EXIT

# Copy all extension files
echo "Copying extension files..."
cp -r "${SCRIPT_DIR}/META-INF" "${BUILD_DIR}/"
cp -r "${SCRIPT_DIR}/python" "${BUILD_DIR}/"
cp -r "${SCRIPT_DIR}/icons" "${BUILD_DIR}/"
cp -r "${SCRIPT_DIR}/dialogs" "${BUILD_DIR}/"
cp -r "${SCRIPT_DIR}/description" "${BUILD_DIR}/"
cp "${SCRIPT_DIR}/description.xml" "${BUILD_DIR}/"
cp "${SCRIPT_DIR}/Addons.xcu" "${BUILD_DIR}/"
cp "${SCRIPT_DIR}/OptionsDialog.xcu" "${BUILD_DIR}/"
cp "${SCRIPT_DIR}/LICENSE.txt" "${BUILD_DIR}/"

# Convert SVG icons to PNG (if ImageMagick is available)
if command -v convert &> /dev/null; then
    echo "Converting SVG icons to PNG..."
    for svg in "${BUILD_DIR}/icons"/*.svg; do
        if [ -f "$svg" ]; then
            base=$(basename "$svg" .svg)
            convert -background none "$svg" "${BUILD_DIR}/icons/${base}.png"
            # Create 16px version
            convert -background none -resize 16x16 "$svg" "${BUILD_DIR}/icons/${base/26/16}.png"
        fi
    done
else
    echo "Warning: ImageMagick not found, skipping SVG to PNG conversion"
    echo "Icons will use SVG format (may not work in older LibreOffice versions)"
fi

# Create the OXT package (ZIP with .oxt extension)
echo "Creating OXT package..."
cd "${BUILD_DIR}"
zip -r -q "${OUTPUT_FILE}" .

echo ""
echo "Build complete!"
echo "Extension package: ${OUTPUT_FILE}"
echo ""
echo "To install:"
echo "  1. Open PreOffice/LibreOffice"
echo "  2. Go to Tools > Extension Manager"
echo "  3. Click 'Add' and select the .oxt file"
echo "  4. Restart PreOffice/LibreOffice"
