#!/bin/bash
#
# PreOffice Build Script
# Applies branding and prepares/builds LibreOffice as PreOffice
#
# Usage:
#   ./build.sh prepare    # Apply branding and configure (no compile)
#   ./build.sh build      # Full build
#   ./build.sh clean      # Clean build artifacts
#   ./build.sh package    # Create installers
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CORE_DIR="$SCRIPT_DIR/core"
PRESEARCH_DIR="$SCRIPT_DIR/presearch"
BRAND_DIR="$PRESEARCH_DIR/brand"

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin) OS="macos" ;;
        Linux) OS="linux" ;;
        MINGW*|MSYS*|CYGWIN*) OS="windows" ;;
        *) error "Unsupported OS: $(uname -s)" ;;
    esac
    info "Detected OS: $OS"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."

    # Check for required tools
    local missing=()

    command -v git >/dev/null 2>&1 || missing+=("git")
    command -v python3 >/dev/null 2>&1 || missing+=("python3")
    command -v make >/dev/null 2>&1 || missing+=("make")

    case "$OS" in
        macos)
            command -v xcodebuild >/dev/null 2>&1 || missing+=("Xcode")
            ;;
        linux)
            command -v gcc >/dev/null 2>&1 || missing+=("gcc")
            command -v g++ >/dev/null 2>&1 || missing+=("g++")
            ;;
        windows)
            # Check for Visual Studio
            ;;
    esac

    if [[ ${#missing[@]} -gt 0 ]]; then
        error "Missing prerequisites: ${missing[*]}"
    fi

    success "All prerequisites found"
}

# Apply branding patches
apply_branding() {
    info "Applying PreOffice branding..."

    cd "$CORE_DIR"

    # Apply patches if not already applied
    for patch in "$BRAND_DIR/patches/"*.patch; do
        if [[ -f "$patch" ]]; then
            patch_name=$(basename "$patch")
            if ! git log --oneline | grep -q "${patch_name%.patch}"; then
                info "Applying patch: $patch_name"
                git apply "$patch" 2>/dev/null || warn "Patch may already be applied: $patch_name"
            fi
        fi
    done

    # Copy splash screens
    if [[ -d "$BRAND_DIR/splash" ]]; then
        local splash_dest="$CORE_DIR/icon-themes/colibre/brand"
        mkdir -p "$splash_dest"
        cp "$BRAND_DIR/splash/intro.png" "$splash_dest/" 2>/dev/null || true
        cp "$BRAND_DIR/splash/intro-highres.png" "$splash_dest/" 2>/dev/null || true
        success "Copied splash screens"
    fi

    # Copy icon theme
    if [[ -d "$PRESEARCH_DIR/ui/icon-theme" ]]; then
        local icon_dest="$CORE_DIR/icon-themes/presearch"
        mkdir -p "$icon_dest/cmd"
        cp -r "$PRESEARCH_DIR/ui/icon-theme/cmd/"*.svg "$icon_dest/cmd/" 2>/dev/null || true
        cp "$PRESEARCH_DIR/ui/icon-theme/links.txt" "$icon_dest/" 2>/dev/null || true
        success "Copied icon theme"
    fi

    # Update product name in key files
    info "Updating product name..."

    # configure.ac
    if [[ -f configure.ac ]]; then
        sed -i.bak 's/AC_INIT(\[LibreOffice\]/AC_INIT([PreOffice]/' configure.ac
        rm -f configure.ac.bak
    fi

    # openoffice.lst.in (branding variables)
    if [[ -f instsetoo_native/inc_openoffice/openoffice.lst.in ]]; then
        local lst_file="instsetoo_native/inc_openoffice/openoffice.lst.in"
        sed -i.bak 's/WINDOWSBASISROOTNAME LibreOffice/WINDOWSBASISROOTNAME PreOffice/' "$lst_file"
        sed -i.bak 's/UNIXBASISROOTNAME libreoffice/UNIXBASISROOTNAME preoffice/' "$lst_file"
        sed -i.bak 's/PROGRESSBARCOLOR 0,0,0/PROGRESSBARCOLOR 45,142,255/' "$lst_file"
        rm -f "$lst_file.bak"
    fi

    success "Branding applied"
}

# Copy Notebookbar configuration
apply_notebookbar() {
    info "Applying Notebookbar customization..."

    local nb_src="$PRESEARCH_DIR/ui/notebookbar"
    local nb_dest="$CORE_DIR/officecfg/registry/data/org/openoffice/Office/UI"

    if [[ -d "$nb_src" ]]; then
        mkdir -p "$nb_dest"
        cp "$nb_src/"*.xcu "$nb_dest/" 2>/dev/null || true
        success "Notebookbar configuration copied"
    fi
}

# Configure build
configure_build() {
    info "Configuring build..."

    cd "$CORE_DIR"

    # Copy autogen.input
    if [[ -f "$SCRIPT_DIR/autogen.input" ]]; then
        cp "$SCRIPT_DIR/autogen.input" ./
        success "Copied autogen.input"
    fi

    # Run autogen.sh
    if [[ -f autogen.sh ]]; then
        info "Running autogen.sh..."
        ./autogen.sh
        success "Configuration complete"
    else
        error "autogen.sh not found in core directory"
    fi
}

# Prepare (no compile)
prepare() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║      PreOffice Build Preparation           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo ""

    detect_os
    check_prerequisites
    apply_branding
    apply_notebookbar
    configure_build

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║      Preparation Complete!                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo "To build PreOffice, run:"
    echo "  cd core && make"
    echo ""
    echo "Or use: ./build.sh build"
    echo ""
}

# Full build
build() {
    prepare

    info "Starting build..."
    cd "$CORE_DIR"

    # Get CPU count for parallel build
    local cpus
    case "$OS" in
        macos) cpus=$(sysctl -n hw.ncpu) ;;
        linux) cpus=$(nproc) ;;
        windows) cpus=$NUMBER_OF_PROCESSORS ;;
    esac

    make -j"$cpus"

    success "Build complete!"
}

# Clean
clean() {
    info "Cleaning build artifacts..."
    cd "$CORE_DIR"

    make clean 2>/dev/null || true
    rm -rf workdir instdir

    success "Clean complete"
}

# Package
package() {
    info "Creating packages..."

    cd "$CORE_DIR"

    case "$OS" in
        macos)
            make mac-app-store-package 2>/dev/null || make pkg
            ;;
        linux)
            make rpm 2>/dev/null || make deb
            ;;
        windows)
            make msi
            ;;
    esac

    success "Packaging complete"
}

# Show help
show_help() {
    echo "PreOffice Build Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  prepare    Apply branding and configure (no compile)"
    echo "  build      Full build (prepare + compile)"
    echo "  clean      Clean build artifacts"
    echo "  package    Create installers"
    echo "  help       Show this help"
    echo ""
}

# Main
case "${1:-help}" in
    prepare) prepare ;;
    build) build ;;
    clean) clean ;;
    package) package ;;
    help|--help|-h) show_help ;;
    *) error "Unknown command: $1. Use '$0 help' for usage." ;;
esac
