#!/bin/bash
# Apply PreOffice branding to LibreOffice core
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
CORE_DIR="$REPO_ROOT/core"
BRAND_DIR="$SCRIPT_DIR"

echo "PreOffice Branding Application"
echo "==============================="
echo ""

# Check if core exists
if [ ! -d "$CORE_DIR" ]; then
    echo "Error: core/ directory not found at $CORE_DIR"
    echo "Please clone LibreOffice core first."
    exit 1
fi

cd "$CORE_DIR"

# 1. Apply product name changes to configure.ac
echo "[1/5] Applying product name changes..."
if grep -q "LibreOffice" configure.ac; then
    sed -i.bak 's/AC_INIT(\[LibreOffice\]/AC_INIT([PreOffice]/' configure.ac
    sed -i.bak 's|http://documentfoundation.org/|https://presearch.com/preoffice|' configure.ac
    echo "  - configure.ac updated"
else
    echo "  - configure.ac already modified or different format"
fi

# 2. Apply changes to openoffice.lst.in
echo "[2/5] Applying installer branding..."
LST_FILE="instsetoo_native/util/openoffice.lst.in"
if [ -f "$LST_FILE" ]; then
    sed -i.bak 's/WINDOWSBASISROOTNAME LibreOffice/WINDOWSBASISROOTNAME PreOffice/' "$LST_FILE"
    sed -i.bak 's/UNIXBASISROOTNAME libreoffice/UNIXBASISROOTNAME preoffice/' "$LST_FILE"
    sed -i.bak 's/BASISPACKAGEPREFIX libobasis/BASISPACKAGEPREFIX preoffice/' "$LST_FILE"
    sed -i.bak 's/UREPACKAGEPREFIX libreoffice/UREPACKAGEPREFIX preoffice/' "$LST_FILE"
    sed -i.bak 's/SOLSUREPACKAGEPREFIX libreoffice/SOLSUREPACKAGEPREFIX preoffice/' "$LST_FILE"
    # Update progress bar color to Presearch blue (RGB: 45, 142, 255)
    sed -i.bak 's/PROGRESSBARCOLOR 0,0,0/PROGRESSBARCOLOR 45,142,255/' "$LST_FILE"
    sed -i.bak 's/PROGRESSFRAMECOLOR 102,102,102/PROGRESSFRAMECOLOR 45,142,255/' "$LST_FILE"
    # Disable update URL
    sed -i.bak 's|UPDATEURL https://update.libreoffice.org/check.php|UPDATEURL|' "$LST_FILE"
    # Update download names
    sed -i.bak 's/downloadname    LibreOffice_/downloadname    PreOffice_/' "$LST_FILE"
    sed -i.bak 's/langpackdownloadname    LibreOffice_/langpackdownloadname    PreOffice_/' "$LST_FILE"
    sed -i.bak 's/helppackdownloadname    LibreOffice_/helppackdownloadname    PreOffice_/' "$LST_FILE"
    echo "  - openoffice.lst.in updated"
fi

# 3. Copy splash screen if available
echo "[3/5] Copying splash screen..."
SPLASH_DIR="$BRAND_DIR/splash"
TARGET_BRAND="$CORE_DIR/icon-themes/colibre/brand"
if [ -d "$SPLASH_DIR" ] && [ -f "$SPLASH_DIR/intro.png" ]; then
    cp "$SPLASH_DIR/intro.png" "$TARGET_BRAND/"
    [ -f "$SPLASH_DIR/intro-highres.png" ] && cp "$SPLASH_DIR/intro-highres.png" "$TARGET_BRAND/"
    echo "  - Splash screens copied"
else
    echo "  - No custom splash screens found (using default)"
    echo "    To add: create $SPLASH_DIR/intro.png (661x169)"
fi

# 4. Set privacy-friendly defaults
echo "[4/5] Setting privacy defaults..."
# These would be in officecfg but require more complex XML editing
# For now, we rely on configure options
echo "  - Privacy defaults will be set via configure options"

# 5. Clean up backup files
echo "[5/5] Cleaning up..."
find . -name "*.bak" -type f -delete 2>/dev/null || true
echo "  - Backup files removed"

echo ""
echo "Branding applied successfully!"
echo ""
echo "Next steps:"
echo "  1. Create splash screen images in presearch/brand/splash/"
echo "  2. Run: cd core && ./autogen.sh --with-product-name='PreOffice' --enable-release-build"
echo "  3. Run: make"
echo ""
echo "Note: 'Based on LibreOffice technology' attribution is maintained in About dialog."
