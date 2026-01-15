#!/bin/bash
# Build script for Presearch icon theme

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_DIR="$(dirname "$SCRIPT_DIR")"
SRC_DIR="$THEME_DIR/src-svg"
BUILD_DIR="$THEME_DIR/build"
DIST_DIR="$THEME_DIR/dist"

echo "Building Presearch icon theme..."

# Clean build directory
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/cmd" "$BUILD_DIR/res"

# Check for svgo
if command -v svgo &> /dev/null; then
    USE_SVGO=true
    echo "Using svgo for SVG optimization"
else
    USE_SVGO=false
    echo "Warning: svgo not found. SVGs will not be optimized."
    echo "Install with: npm install -g svgo"
fi

# Process SVG files
process_svg() {
    local src="$1"
    local dest="$2"

    if [ "$USE_SVGO" = true ]; then
        svgo -i "$src" -o "$dest" --quiet
    else
        cp "$src" "$dest"
    fi
}

# Copy and optimize SVGs from src-svg
if [ -d "$SRC_DIR" ]; then
    echo "Processing source SVGs..."

    # Process root level icons
    for svg in "$SRC_DIR"/*.svg; do
        [ -f "$svg" ] || continue
        filename=$(basename "$svg")
        process_svg "$svg" "$BUILD_DIR/$filename"
    done

    # Process cmd icons
    if [ -d "$SRC_DIR/cmd" ]; then
        for svg in "$SRC_DIR/cmd"/*.svg; do
            [ -f "$svg" ] || continue
            filename=$(basename "$svg")
            process_svg "$svg" "$BUILD_DIR/cmd/$filename"
        done
    fi

    # Process res icons
    if [ -d "$SRC_DIR/res" ]; then
        for svg in "$SRC_DIR/res"/*.svg; do
            [ -f "$svg" ] || continue
            filename=$(basename "$svg")
            process_svg "$svg" "$BUILD_DIR/res/$filename"
        done
    fi
fi

# Copy links.txt for fallback
if [ -f "$THEME_DIR/links.txt" ]; then
    cp "$THEME_DIR/links.txt" "$BUILD_DIR/"
fi

# Create the zip file
mkdir -p "$DIST_DIR"
cd "$BUILD_DIR"
zip -r "$DIST_DIR/images_presearch.zip" .

echo "Build complete: $DIST_DIR/images_presearch.zip"

# Show stats
echo ""
echo "Theme contents:"
find . -type f | wc -l | xargs echo "  Total files:"
find . -name "*.svg" | wc -l | xargs echo "  SVG icons:"
