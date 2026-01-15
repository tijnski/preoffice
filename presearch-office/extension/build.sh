#!/bin/bash
# Build script for Presearch Tools extension

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR/src"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"

VERSION="1.0.0"
EXTENSION_NAME="presearch-tools"

echo "Building Presearch Tools extension v${VERSION}..."

# Clean and create directories
rm -rf "$BUILD_DIR" "$DIST_DIR"
mkdir -p "$BUILD_DIR" "$DIST_DIR"

# Copy extension files to build directory
echo "Copying extension files..."
cp "$SRC_DIR/description.xml" "$BUILD_DIR/"
cp "$SRC_DIR/Addons.xcu" "$BUILD_DIR/"
cp "$SRC_DIR/LICENSE.txt" "$BUILD_DIR/"

# Copy META-INF
cp -r "$SRC_DIR/META-INF" "$BUILD_DIR/"

# Copy description
cp -r "$SRC_DIR/description" "$BUILD_DIR/"

# Copy Python scripts
mkdir -p "$BUILD_DIR/python"
cp "$SRC_DIR/python/"*.py "$BUILD_DIR/python/"

# Copy icons if they exist
if [ -d "$SRC_DIR/icons" ] && [ "$(ls -A "$SRC_DIR/icons" 2>/dev/null)" ]; then
    cp -r "$SRC_DIR/icons" "$BUILD_DIR/"
else
    mkdir -p "$BUILD_DIR/icons"
    echo "Note: No icons found in src/icons/"
fi

# Copy templates if they exist
if [ -d "$SRC_DIR/templates" ] && [ "$(ls -A "$SRC_DIR/templates" 2>/dev/null)" ]; then
    cp -r "$SRC_DIR/templates" "$BUILD_DIR/"
fi

# Copy config if it exists
if [ -d "$SRC_DIR/config" ] && [ "$(ls -A "$SRC_DIR/config" 2>/dev/null)" ]; then
    cp -r "$SRC_DIR/config" "$BUILD_DIR/"
fi

# Create the .oxt file (it's just a zip)
echo "Creating .oxt package..."
cd "$BUILD_DIR"
zip -r "$DIST_DIR/${EXTENSION_NAME}-${VERSION}.oxt" . -x "*.DS_Store"

# Also create a convenience symlink to latest
cd "$DIST_DIR"
ln -sf "${EXTENSION_NAME}-${VERSION}.oxt" "${EXTENSION_NAME}.oxt"

echo ""
echo "Build complete!"
echo "Output: $DIST_DIR/${EXTENSION_NAME}-${VERSION}.oxt"
echo ""
echo "To install:"
echo "  1. Open LibreOffice"
echo "  2. Go to Tools -> Extension Manager"
echo "  3. Click 'Add' and select the .oxt file"
echo "  4. Restart LibreOffice"
