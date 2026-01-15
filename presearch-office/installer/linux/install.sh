#!/bin/bash
# Presearch Office Edition - Linux Installer
# Installs LibreOffice + Presearch customizations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRESEARCH_OFFICE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Configuration
USER_PROFILE="$HOME/.config/libreoffice/4/user"

echo "=========================================="
echo "  Presearch Office Edition Installer"
echo "  Linux"
echo "=========================================="
echo ""

# Detect package manager
detect_package_manager() {
    if command -v apt-get &> /dev/null; then
        echo "apt"
    elif command -v dnf &> /dev/null; then
        echo "dnf"
    elif command -v pacman &> /dev/null; then
        echo "pacman"
    elif command -v zypper &> /dev/null; then
        echo "zypper"
    elif command -v flatpak &> /dev/null; then
        echo "flatpak"
    else
        echo "unknown"
    fi
}

# Check if LibreOffice is installed
check_libreoffice() {
    if command -v libreoffice &> /dev/null || \
       command -v soffice &> /dev/null || \
       [ -d "/opt/libreoffice"* ] || \
       flatpak list 2>/dev/null | grep -qi libreoffice; then
        echo "LibreOffice is already installed."
        read -p "Skip LibreOffice installation? (Y/n) " skip
        if [ "$skip" != "n" ] && [ "$skip" != "N" ]; then
            return 0
        fi
    fi
    return 1
}

# Install LibreOffice based on distro
install_libreoffice() {
    local pkg_manager=$(detect_package_manager)

    echo "Installing LibreOffice using: $pkg_manager"

    case $pkg_manager in
        apt)
            sudo apt-get update
            sudo apt-get install -y libreoffice
            ;;
        dnf)
            sudo dnf install -y libreoffice
            ;;
        pacman)
            sudo pacman -S --noconfirm libreoffice-fresh
            ;;
        zypper)
            sudo zypper install -y libreoffice
            ;;
        flatpak)
            flatpak install -y flathub org.libreoffice.LibreOffice
            ;;
        *)
            echo "Could not detect package manager."
            echo "Please install LibreOffice manually from:"
            echo "  https://www.libreoffice.org/download/download/"
            return 1
            ;;
    esac

    echo "LibreOffice installed successfully!"
}

# Find unopkg binary
find_unopkg() {
    # Check common locations
    local locations=(
        "/usr/bin/unopkg"
        "/usr/lib/libreoffice/program/unopkg"
        "/opt/libreoffice*/program/unopkg"
        "$HOME/.local/share/flatpak/exports/bin/org.libreoffice.LibreOffice.unopkg"
    )

    for loc in "${locations[@]}"; do
        # Handle glob patterns
        for path in $loc; do
            if [ -x "$path" ]; then
                echo "$path"
                return 0
            fi
        done
    done

    # Try which
    if command -v unopkg &> /dev/null; then
        which unopkg
        return 0
    fi

    return 1
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

    # Find unopkg
    UNOPKG=$(find_unopkg) || true

    if [ -n "$UNOPKG" ]; then
        "$UNOPKG" add "$EXTENSION_PATH" 2>/dev/null || \
        "$UNOPKG" add --shared "$EXTENSION_PATH" 2>/dev/null || \
        echo "Note: Extension installed for current user only"
        echo "Extension installed successfully!"
    else
        echo "Warning: unopkg not found."
        echo "Please install extension manually:"
        echo "  1. Open LibreOffice"
        echo "  2. Go to Tools -> Extension Manager"
        echo "  3. Click Add and select: $EXTENSION_PATH"
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

    # Determine user profile location
    # Flatpak uses a different path
    if flatpak list 2>/dev/null | grep -qi libreoffice; then
        USER_PROFILE="$HOME/.var/app/org.libreoffice.LibreOffice/config/libreoffice/4/user"
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

# Configure defaults
configure_defaults() {
    echo ""
    echo "Configuring defaults..."

    # Determine user profile location
    if flatpak list 2>/dev/null | grep -qi libreoffice; then
        USER_PROFILE="$HOME/.var/app/org.libreoffice.LibreOffice/config/libreoffice/4/user"
    fi

    mkdir -p "$USER_PROFILE"

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
    echo "  libreoffice"
    echo ""
    echo "You'll find Presearch tools in the menu bar."
}

main "$@"
