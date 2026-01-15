#!/bin/bash
# =============================================================================
# PreOffice RPM Package Builder
# Creates an .rpm package for Fedora/RHEL/CentOS/openSUSE
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
PACKAGE_NAME="preoffice"
PACKAGE_VERSION="1.0.0"
PACKAGE_RELEASE="1"
PACKAGE_ARCH="x86_64"
MAINTAINER="Presearch <support@presearch.com>"
DESCRIPTION="PreOffice - AI-Powered Office Suite by Presearch"
LICENSE="MIT"
URL="https://presearch.com/preoffice"

# Directories
BUILD_DIR="${PROJECT_ROOT}/build/linux/rpm"
SOURCE_DIR="${PROJECT_ROOT}/instdir"
DIST_DIR="${PROJECT_ROOT}/dist"
RPM_BUILD_ROOT="${BUILD_DIR}/BUILDROOT/${PACKAGE_NAME}-${PACKAGE_VERSION}-${PACKAGE_RELEASE}.${PACKAGE_ARCH}"

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
    if ! command -v rpmbuild &> /dev/null; then
        log_error "rpmbuild not found"
        log_info "Install with:"
        log_info "  Fedora/RHEL: sudo dnf install rpm-build rpmdevtools"
        log_info "  openSUSE: sudo zypper install rpm-build"
        exit 1
    fi

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

prepare_rpm_structure() {
    log_info "Preparing RPM build structure..."

    # Create RPM directory structure
    mkdir -p "$BUILD_DIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS,BUILDROOT}

    log_success "RPM structure created"
}

create_spec_file() {
    log_info "Creating spec file..."

    cat > "$BUILD_DIR/SPECS/${PACKAGE_NAME}.spec" << EOF
Name:           ${PACKAGE_NAME}
Version:        ${PACKAGE_VERSION}
Release:        ${PACKAGE_RELEASE}%{?dist}
Summary:        ${DESCRIPTION}

License:        ${LICENSE}
URL:            ${URL}

BuildArch:      ${PACKAGE_ARCH}

Requires:       glibc >= 2.17
Requires:       libstdc++
Requires:       libX11
Requires:       libXext
Requires:       libXinerama
Requires:       libXrandr
Requires:       freetype
Requires:       fontconfig
Requires:       zlib
Requires:       cups-libs

Recommends:     liberation-fonts
Recommends:     google-noto-sans-fonts

Suggests:       hunspell
Suggests:       hyphen

Provides:       office-suite
Conflicts:      libreoffice-core

%description
PreOffice is a customized LibreOffice distribution by Presearch featuring:

- PrePanda AI Assistant for intelligent document assistance
- Modern UI with customizable Notebookbar/Ribbon interface
- Presearch branding and color schemes
- Privacy-focused AI powered by Venice.ai

Includes Writer (word processor), Calc (spreadsheet), Impress (presentations),
and Draw (vector graphics).

%prep
# Nothing to prepare, we're copying built files

%build
# Nothing to build, using pre-built binaries

%install
rm -rf %{buildroot}

# Create directory structure
mkdir -p %{buildroot}/opt/preoffice
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor/{22x22,48x48,128x128}/apps
mkdir -p %{buildroot}/usr/share/mime/packages
mkdir -p %{buildroot}/usr/bin

# Copy files (this is done by the build script)
cp -R ${SOURCE_DIR}/* %{buildroot}/opt/preoffice/ || true

# Copy customizations
if [[ -d "${PROJECT_ROOT}/presearch" ]]; then
    # Branding
    if [[ -d "${PROJECT_ROOT}/presearch/branding" ]]; then
        mkdir -p %{buildroot}/opt/preoffice/share/gallery
        cp -R ${PROJECT_ROOT}/presearch/branding/* %{buildroot}/opt/preoffice/share/gallery/ || true
    fi

    # Templates
    if [[ -d "${PROJECT_ROOT}/presearch/templates" ]]; then
        mkdir -p %{buildroot}/opt/preoffice/share/template
        cp -R ${PROJECT_ROOT}/presearch/templates/* %{buildroot}/opt/preoffice/share/template/ || true
    fi

    # Extension
    if [[ -f "${PROJECT_ROOT}/presearch/extension/PreOffice-1.0.0.oxt" ]]; then
        mkdir -p %{buildroot}/opt/preoffice/share/extensions
        cp ${PROJECT_ROOT}/presearch/extension/PreOffice-1.0.0.oxt %{buildroot}/opt/preoffice/share/extensions/
    fi
fi

%post
# Update desktop database
update-desktop-database -q /usr/share/applications 2>/dev/null || true

# Update icon cache
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true

# Update MIME database
update-mime-database /usr/share/mime 2>/dev/null || true

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

%preun
# Remove symbolic links
rm -f /usr/bin/preoffice
rm -f /usr/bin/preoffice-writer
rm -f /usr/bin/preoffice-calc
rm -f /usr/bin/preoffice-impress
rm -f /usr/bin/preoffice-draw

%postun
# Update desktop database
update-desktop-database -q /usr/share/applications 2>/dev/null || true

# Update icon cache
gtk-update-icon-cache -f -t /usr/share/icons/hicolor 2>/dev/null || true

%files
%defattr(-,root,root,-)
/opt/preoffice
/usr/share/applications/*.desktop
/usr/share/icons/hicolor/*/apps/*

%changelog
* $(date "+%a %b %d %Y") Presearch <support@presearch.com> - ${PACKAGE_VERSION}-${PACKAGE_RELEASE}
- Initial release of PreOffice
- Includes PrePanda AI Assistant
- Custom Notebookbar/Ribbon UI
- Presearch branding
EOF

    log_success "Spec file created"
}

create_desktop_files() {
    log_info "Creating desktop files for RPM..."

    mkdir -p "$RPM_BUILD_ROOT/usr/share/applications"

    # Writer
    cat > "$RPM_BUILD_ROOT/usr/share/applications/preoffice-writer.desktop" << EOF
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
MimeType=application/vnd.oasis.opendocument.text;application/msword;application/vnd.openxmlformats-officedocument.wordprocessingml.document;
StartupNotify=true
EOF

    # Calc
    cat > "$RPM_BUILD_ROOT/usr/share/applications/preoffice-calc.desktop" << EOF
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
StartupNotify=true
EOF

    # Impress
    cat > "$RPM_BUILD_ROOT/usr/share/applications/preoffice-impress.desktop" << EOF
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
StartupNotify=true
EOF

    # Draw
    cat > "$RPM_BUILD_ROOT/usr/share/applications/preoffice-draw.desktop" << EOF
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
StartupNotify=true
EOF

    log_success "Desktop files created"
}

copy_files_to_buildroot() {
    log_info "Copying files to BUILDROOT..."

    mkdir -p "$RPM_BUILD_ROOT/opt/preoffice"
    cp -R "$SOURCE_DIR/"* "$RPM_BUILD_ROOT/opt/preoffice/" 2>/dev/null || {
        log_warning "Some files could not be copied"
    }

    # Copy customizations
    if [[ -d "$PROJECT_ROOT/presearch" ]]; then
        # Branding
        if [[ -d "$PROJECT_ROOT/presearch/branding" ]]; then
            mkdir -p "$RPM_BUILD_ROOT/opt/preoffice/share/gallery"
            cp -R "$PROJECT_ROOT/presearch/branding/"* "$RPM_BUILD_ROOT/opt/preoffice/share/gallery/" 2>/dev/null || true
        fi

        # Templates
        if [[ -d "$PROJECT_ROOT/presearch/templates" ]]; then
            mkdir -p "$RPM_BUILD_ROOT/opt/preoffice/share/template"
            cp -R "$PROJECT_ROOT/presearch/templates/"* "$RPM_BUILD_ROOT/opt/preoffice/share/template/" 2>/dev/null || true
        fi

        # Extension
        if [[ -f "$PROJECT_ROOT/presearch/extension/PreOffice-1.0.0.oxt" ]]; then
            mkdir -p "$RPM_BUILD_ROOT/opt/preoffice/share/extensions"
            cp "$PROJECT_ROOT/presearch/extension/PreOffice-1.0.0.oxt" "$RPM_BUILD_ROOT/opt/preoffice/share/extensions/"
        fi
    fi

    # Create icon directories
    mkdir -p "$RPM_BUILD_ROOT/usr/share/icons/hicolor/"{22x22,48x48,128x128}"/apps"

    log_success "Files copied to BUILDROOT"
}

build_rpm() {
    log_info "Building RPM package..."

    mkdir -p "$DIST_DIR"

    # Build the RPM
    rpmbuild --define "_topdir $BUILD_DIR" \
             --define "_builddir $BUILD_DIR/BUILD" \
             --define "_rpmdir $BUILD_DIR/RPMS" \
             --define "_sourcedir $BUILD_DIR/SOURCES" \
             --define "_specdir $BUILD_DIR/SPECS" \
             --define "_srcrpmdir $BUILD_DIR/SRPMS" \
             --define "_buildrootdir $BUILD_DIR/BUILDROOT" \
             -bb "$BUILD_DIR/SPECS/${PACKAGE_NAME}.spec"

    # Copy the RPM to dist
    find "$BUILD_DIR/RPMS" -name "*.rpm" -exec cp {} "$DIST_DIR/" \;

    local RPM_FILE=$(find "$DIST_DIR" -name "*.rpm" -type f | head -n 1)
    if [[ -n "$RPM_FILE" ]]; then
        log_success "Package built: $RPM_FILE"
        log_info "Size: $(du -h "$RPM_FILE" | cut -f1)"
    else
        log_error "RPM file not found after build"
        exit 1
    fi
}

show_help() {
    echo "PreOffice RPM Package Builder"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build      Build the .rpm package (default)"
    echo "  clean      Remove build artifacts"
    echo "  help       Show this help message"
    echo ""
    echo "Prerequisites:"
    echo "  - rpmbuild (dnf install rpm-build rpmdevtools)"
    echo "  - LibreOffice built in $SOURCE_DIR"
}

# =============================================================================
# Main
# =============================================================================

case "${1:-build}" in
    build)
        check_prerequisites
        clean
        prepare_rpm_structure
        copy_files_to_buildroot
        create_desktop_files
        create_spec_file
        build_rpm
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
