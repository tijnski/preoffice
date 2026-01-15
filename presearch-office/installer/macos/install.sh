#!/bin/bash
# Presearch Office Edition - macOS Installer
# Installs LibreOffice + Presearch customizations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRESEARCH_OFFICE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Configuration
LO_VERSION="24.8.4"
LO_DMG_URL="https://download.documentfoundation.org/libreoffice/stable/${LO_VERSION}/mac/x86_64/LibreOffice_${LO_VERSION}_MacOS_x86-64.dmg"
LO_INSTALL_PATH="/Applications/LibreOffice.app"
USER_PROFILE="$HOME/Library/Application Support/LibreOffice/4/user"

echo "=========================================="
echo "  Presearch Office Edition Installer"
echo "  macOS"
echo "=========================================="
echo ""

# Check if LibreOffice is already installed
check_libreoffice() {
    if [ -d "$LO_INSTALL_PATH" ]; then
        echo "LibreOffice is already installed at: $LO_INSTALL_PATH"
        read -p "Skip LibreOffice installation? (Y/n) " skip
        if [ "$skip" != "n" ] && [ "$skip" != "N" ]; then
            return 0
        fi
    fi
    return 1
}

# Download and install LibreOffice
install_libreoffice() {
    echo "Downloading LibreOffice ${LO_VERSION}..."

    TEMP_DIR=$(mktemp -d)
    DMG_PATH="$TEMP_DIR/LibreOffice.dmg"

    curl -L -o "$DMG_PATH" "$LO_DMG_URL"

    echo "Mounting DMG..."
    MOUNT_POINT=$(hdiutil attach "$DMG_PATH" -nobrowse | grep "/Volumes" | awk '{print $NF}')

    echo "Installing LibreOffice..."
    cp -R "$MOUNT_POINT/LibreOffice.app" /Applications/

    echo "Cleaning up..."
    hdiutil detach "$MOUNT_POINT"
    rm -rf "$TEMP_DIR"

    echo "LibreOffice installed successfully!"
}

# Install Presearch extension
install_extension() {
    echo ""
    echo "Installing Presearch Tools extension..."

    EXTENSION_PATH="$PRESEARCH_OFFICE_DIR/extension/dist/presearch-tools.oxt"

    if [ ! -f "$EXTENSION_PATH" ]; then
        echo "Building extension first..."
        cd "$PRESEARCH_OFFICE_DIR/extension"
        ./build.sh
    fi

    # Use unopkg to install the extension
    UNOPKG="$LO_INSTALL_PATH/Contents/MacOS/unopkg"

    if [ -f "$UNOPKG" ]; then
        "$UNOPKG" add --shared "$EXTENSION_PATH" 2>/dev/null || \
        "$UNOPKG" add "$EXTENSION_PATH"
        echo "Extension installed successfully!"
    else
        echo "Warning: unopkg not found. Please install extension manually."
        echo "Extension path: $EXTENSION_PATH"
    fi
}

# Install icon theme
install_icon_theme() {
    echo ""
    echo "Installing Presearch icon theme..."

    THEME_PATH="$PRESEARCH_OFFICE_DIR/icon-theme/dist/images_presearch.zip"

    if [ ! -f "$THEME_PATH" ]; then
        echo "Building icon theme first..."
        cd "$PRESEARCH_OFFICE_DIR/icon-theme"
        ./tools/build.sh
    fi

    # Create user config directory if it doesn't exist
    mkdir -p "$USER_PROFILE/config"

    # Copy theme
    if [ -f "$THEME_PATH" ]; then
        cp "$THEME_PATH" "$USER_PROFILE/config/"
        echo "Icon theme installed successfully!"
    else
        echo "Warning: Icon theme not found at $THEME_PATH"
    fi
}

# Set Presearch as default icon theme
configure_defaults() {
    echo ""
    echo "Configuring defaults..."

    # Create registrymodifications.xcu if it doesn't exist
    REGISTRY_FILE="$USER_PROFILE/registrymodifications.xcu"

    if [ ! -f "$REGISTRY_FILE" ]; then
        mkdir -p "$(dirname "$REGISTRY_FILE")"
        cat > "$REGISTRY_FILE" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
</oor:items>
EOF
    fi

    echo "Default configuration applied."
    echo "Note: To set Presearch icon theme, go to:"
    echo "  Tools -> Options -> View -> Icon Theme -> Presearch"
}

# Main installation flow
main() {
    echo "This installer will:"
    echo "  1. Install LibreOffice (if not present)"
    echo "  2. Install Presearch Tools extension"
    echo "  3. Install Presearch icon theme"
    echo "  4. Configure defaults"
    echo ""
    read -p "Continue? (Y/n) " confirm

    if [ "$confirm" = "n" ] || [ "$confirm" = "N" ]; then
        echo "Installation cancelled."
        exit 0
    fi

    # Step 1: LibreOffice
    if ! check_libreoffice; then
        install_libreoffice
    fi

    # Step 2: Extension
    install_extension

    # Step 3: Icon Theme
    install_icon_theme

    # Step 4: Defaults
    configure_defaults

    echo ""
    echo "=========================================="
    echo "  Installation Complete!"
    echo "=========================================="
    echo ""
    echo "To start Presearch Office Edition:"
    echo "  open /Applications/LibreOffice.app"
    echo ""
    echo "You'll find Presearch tools in the menu bar."
}

main "$@"
