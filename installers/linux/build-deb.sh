#!/bin/bash
# =============================================================================
# PreOffice Debian Package (.deb) Builder
# Creates a .deb package for Debian/Ubuntu/Linux Mint
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
PACKAGE_NAME="preoffice"
PACKAGE_VERSION="1.0.0"
PACKAGE_REVISION="1"
PACKAGE_ARCH="amd64"
MAINTAINER="Presearch <support@presearch.com>"
DESCRIPTION="PreOffice - AI-Powered Office Suite by Presearch"
HOMEPAGE="https://presearch.com/preoffice"

# Directories
BUILD_DIR="${PROJECT_ROOT}/build/linux/deb"
SOURCE_DIR="${PROJECT_ROOT}/instdir"
DIST_DIR="${PROJECT_ROOT}/dist"
DEB_NAME="${PACKAGE_NAME}_${PACKAGE_VERSION}-${PACKAGE_REVISION}_${PACKAGE_ARCH}.deb"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# Functions
# =============================================================================

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check for required tools
    for tool in dpkg-deb fakeroot; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "$tool not found. Install with: sudo apt install dpkg fakeroot"
            exit 1
        fi
    done

    # Check for LibreOffice build
    if [[ ! -d "$SOURCE_DIR" ]]; then
        log_error "LibreOffice build not found at $SOURCE_DIR"
        exit 1
    fi

    log_success "Prerequisites check complete"
}

clean() {
    log_info "Cleaning previous builds..."
    rm -rf "$BUILD_DIR"
    log_success "Clean complete"
}

prepare_package_structure() {
    log_info "Preparing package structure..."

    # Create directory structure
    mkdir -p "$BUILD_DIR/DEBIAN"
    mkdir -p "$BUILD_DIR/opt/preoffice"
    mkdir -p "$BUILD_DIR/usr/share/applications"
    mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/128x128/apps"
    mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/48x48/apps"
    mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/22x22/apps"
    mkdir -p "$BUILD_DIR/usr/share/mime/packages"
    mkdir -p "$BUILD_DIR/usr/bin"

    log_success "Package structure created"
}

copy_files() {
    log_info "Copying files..."

    # Copy LibreOffice build
    cp -R "$SOURCE_DIR/"* "$BUILD_DIR/opt/preoffice/" 2>/dev/null || {
        log_warning "Some files could not be copied"
    }

    # Copy PreOffice customizations
    if [[ -d "$PROJECT_ROOT/presearch" ]]; then
        log_info "Applying PreOffice customizations..."

        # Branding
        if [[ -d "$PROJECT_ROOT/presearch/branding" ]]; then
            mkdir -p "$BUILD_DIR/opt/preoffice/share/gallery"
            cp -R "$PROJECT_ROOT/presearch/branding/"* "$BUILD_DIR/opt/preoffice/share/gallery/" 2>/dev/null || true
        fi

        # Icons
        if [[ -d "$PROJECT_ROOT/presearch/icons" ]]; then
            cp -R "$PROJECT_ROOT/presearch/icons/"* "$BUILD_DIR/opt/preoffice/share/icons/" 2>/dev/null || true
        fi

        # Templates
        if [[ -d "$PROJECT_ROOT/presearch/templates" ]]; then
            mkdir -p "$BUILD_DIR/opt/preoffice/share/template"
            cp -R "$PROJECT_ROOT/presearch/templates/"* "$BUILD_DIR/opt/preoffice/share/template/" 2>/dev/null || true
        fi

        # Extension
        if [[ -f "$PROJECT_ROOT/presearch/extension/PreOffice-1.0.0.oxt" ]]; then
            mkdir -p "$BUILD_DIR/opt/preoffice/share/extensions"
            cp "$PROJECT_ROOT/presearch/extension/PreOffice-1.0.0.oxt" "$BUILD_DIR/opt/preoffice/share/extensions/"
        fi
    fi

    log_success "Files copied"
}

create_control_file() {
    log_info "Creating control file..."

    # Calculate installed size
    INSTALLED_SIZE=$(du -sk "$BUILD_DIR" | cut -f1)

    cat > "$BUILD_DIR/DEBIAN/control" << EOF
Package: ${PACKAGE_NAME}
Version: ${PACKAGE_VERSION}-${PACKAGE_REVISION}
Section: editors
Priority: optional
Architecture: ${PACKAGE_ARCH}
Installed-Size: ${INSTALLED_SIZE}
Maintainer: ${MAINTAINER}
Homepage: ${HOMEPAGE}
Depends: libc6 (>= 2.17), libgcc1 (>= 1:4.1.1), libstdc++6 (>= 4.1.1), libx11-6, libxext6, libxinerama1, libxrandr2, libfreetype6, libfontconfig1, zlib1g, libcups2
Recommends: fonts-liberation, fonts-noto-core
Suggests: hunspell, hyphen-en-us
Conflicts: libreoffice-core
Replaces: libreoffice-core
Provides: office-suite
Description: ${DESCRIPTION}
 PreOffice is a customized LibreOffice distribution by Presearch featuring:
 .
  - PrePanda AI Assistant for intelligent document assistance
  - Modern UI with customizable Notebookbar/Ribbon interface
  - Presearch branding and color schemes
  - Privacy-focused AI powered by Venice.ai
 .
 Includes Writer (word processor), Calc (spreadsheet), Impress (presentations),
 and Draw (vector graphics).
EOF

    log_success "Control file created"
}

create_scripts() {
    log_info "Creating maintainer scripts..."

    # Post-installation script
    cat > "$BUILD_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

# Update MIME database
if command -v update-mime-database &> /dev/null; then
    update-mime-database /usr/share/mime 2>/dev/null || true
fi

# Install the PrePanda extension
if [[ -f /opt/preoffice/share/extensions/PreOffice-1.0.0.oxt ]]; then
    /opt/preoffice/program/unopkg add --shared /opt/preoffice/share/extensions/PreOffice-1.0.0.oxt 2>/dev/null || true
fi

# Create symbolic links
ln -sf /opt/preoffice/program/soffice /usr/bin/preoffice
ln -sf /opt/preoffice/program/swriter /usr/bin/preoffice-writer
ln -sf /opt/preoffice/program/scalc /usr/bin/preoffice-calc
ln -sf /opt/preoffice/program/simpress /usr/bin/preoffice-impress
ln -sf /opt/preoffice/program/sdraw /usr/bin/preoffice-draw

echo "PreOffice installed successfully!"
echo "You can start PreOffice with: preoffice"

exit 0
EOF

    # Pre-removal script
    cat > "$BUILD_DIR/DEBIAN/prerm" << 'EOF'
#!/bin/bash
set -e

# Remove symbolic links
rm -f /usr/bin/preoffice
rm -f /usr/bin/preoffice-writer
rm -f /usr/bin/preoffice-calc
rm -f /usr/bin/preoffice-impress
rm -f /usr/bin/preoffice-draw

exit 0
EOF

    # Post-removal script
    cat > "$BUILD_DIR/DEBIAN/postrm" << 'EOF'
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database -q /usr/share/applications 2>/dev/null || true
fi

# Update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true
fi

exit 0
EOF

    chmod 755 "$BUILD_DIR/DEBIAN/postinst"
    chmod 755 "$BUILD_DIR/DEBIAN/prerm"
    chmod 755 "$BUILD_DIR/DEBIAN/postrm"

    log_success "Maintainer scripts created"
}

create_desktop_files() {
    log_info "Creating desktop files..."

    # PreOffice Writer
    cat > "$BUILD_DIR/usr/share/applications/preoffice-writer.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PreOffice Writer
GenericName=Word Processor
Comment=Create and edit text documents with PrePanda AI assistance
Exec=/opt/preoffice/program/swriter %U
Icon=preoffice-writer
Terminal=false
Categories=Office;WordProcessor;
MimeType=application/vnd.oasis.opendocument.text;application/msword;application/vnd.openxmlformats-officedocument.wordprocessingml.document;text/rtf;
Keywords=document;text;odt;docx;word;
StartupNotify=true
StartupWMClass=libreoffice-writer
EOF

    # PreOffice Calc
    cat > "$BUILD_DIR/usr/share/applications/preoffice-calc.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PreOffice Calc
GenericName=Spreadsheet
Comment=Create and edit spreadsheets with PrePanda AI assistance
Exec=/opt/preoffice/program/scalc %U
Icon=preoffice-calc
Terminal=false
Categories=Office;Spreadsheet;
MimeType=application/vnd.oasis.opendocument.spreadsheet;application/vnd.ms-excel;application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;
Keywords=spreadsheet;excel;ods;xlsx;
StartupNotify=true
StartupWMClass=libreoffice-calc
EOF

    # PreOffice Impress
    cat > "$BUILD_DIR/usr/share/applications/preoffice-impress.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PreOffice Impress
GenericName=Presentation
Comment=Create and edit presentations with PrePanda AI assistance
Exec=/opt/preoffice/program/simpress %U
Icon=preoffice-impress
Terminal=false
Categories=Office;Presentation;
MimeType=application/vnd.oasis.opendocument.presentation;application/vnd.ms-powerpoint;application/vnd.openxmlformats-officedocument.presentationml.presentation;
Keywords=presentation;slides;odp;pptx;powerpoint;
StartupNotify=true
StartupWMClass=libreoffice-impress
EOF

    # PreOffice Draw
    cat > "$BUILD_DIR/usr/share/applications/preoffice-draw.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=PreOffice Draw
GenericName=Drawing
Comment=Create and edit drawings and diagrams
Exec=/opt/preoffice/program/sdraw %U
Icon=preoffice-draw
Terminal=false
Categories=Office;Graphics;VectorGraphics;
MimeType=application/vnd.oasis.opendocument.graphics;
Keywords=drawing;vector;diagram;odg;
StartupNotify=true
StartupWMClass=libreoffice-draw
EOF

    log_success "Desktop files created"
}

create_icons() {
    log_info "Creating application icons..."

    # Copy icons if they exist, otherwise create placeholders
    local ICON_SOURCE="$PROJECT_ROOT/presearch/icons"

    for size in 22 48 128; do
        local ICON_DIR="$BUILD_DIR/usr/share/icons/hicolor/${size}x${size}/apps"

        for app in writer calc impress draw; do
            if [[ -f "$ICON_SOURCE/preoffice-${app}-${size}.png" ]]; then
                cp "$ICON_SOURCE/preoffice-${app}-${size}.png" "$ICON_DIR/preoffice-${app}.png"
            fi
        done
    done

    log_success "Icons processed"
}

build_deb() {
    log_info "Building .deb package..."

    mkdir -p "$DIST_DIR"

    # Build the package using fakeroot
    fakeroot dpkg-deb --build "$BUILD_DIR" "$DIST_DIR/$DEB_NAME"

    log_success "Package built: $DIST_DIR/$DEB_NAME"
    log_info "Size: $(du -h "$DIST_DIR/$DEB_NAME" | cut -f1)"

    # Verify the package
    log_info "Verifying package..."
    dpkg-deb --info "$DIST_DIR/$DEB_NAME"
}

show_help() {
    echo "PreOffice Debian Package Builder"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build      Build the .deb package (default)"
    echo "  clean      Remove build artifacts"
    echo "  help       Show this help message"
    echo ""
    echo "The package will be created at: $DIST_DIR/$DEB_NAME"
    echo ""
    echo "Prerequisites:"
    echo "  - dpkg-deb and fakeroot (apt install dpkg fakeroot)"
    echo "  - LibreOffice built in $SOURCE_DIR"
}

# =============================================================================
# Main
# =============================================================================

case "${1:-build}" in
    build)
        check_prerequisites
        clean
        prepare_package_structure
        copy_files
        create_control_file
        create_scripts
        create_desktop_files
        create_icons
        build_deb
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
