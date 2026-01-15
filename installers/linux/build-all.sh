#!/bin/bash
# =============================================================================
# PreOffice Linux Package Builder
# Unified script to build DEB and RPM packages
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

detect_distro() {
    if [[ -f /etc/os-release ]]; then
        . /etc/os-release
        echo "$ID"
    elif command -v lsb_release &> /dev/null; then
        lsb_release -si | tr '[:upper:]' '[:lower:]'
    else
        echo "unknown"
    fi
}

build_for_distro() {
    local distro=$(detect_distro)

    log_info "Detected distribution: $distro"

    case "$distro" in
        ubuntu|debian|linuxmint|pop|elementary|zorin)
            log_info "Building DEB package for Debian-based system..."
            "$SCRIPT_DIR/build-deb.sh" "$@"
            ;;
        fedora|rhel|centos|rocky|alma|oracle)
            log_info "Building RPM package for Red Hat-based system..."
            "$SCRIPT_DIR/build-rpm.sh" "$@"
            ;;
        opensuse*|suse*)
            log_info "Building RPM package for SUSE-based system..."
            "$SCRIPT_DIR/build-rpm.sh" "$@"
            ;;
        arch|manjaro|endeavouros)
            log_warning "Arch-based system detected"
            log_info "Use makepkg with PKGBUILD (not yet implemented)"
            log_info "Falling back to DEB package..."
            "$SCRIPT_DIR/build-deb.sh" "$@"
            ;;
        *)
            log_warning "Unknown distribution: $distro"
            log_info "Attempting to build DEB package..."
            "$SCRIPT_DIR/build-deb.sh" "$@"
            ;;
    esac
}

build_all() {
    log_info "Building all Linux packages..."

    local has_dpkg=false
    local has_rpm=false

    if command -v dpkg-deb &> /dev/null; then
        has_dpkg=true
    fi

    if command -v rpmbuild &> /dev/null; then
        has_rpm=true
    fi

    if [[ "$has_dpkg" == "true" ]]; then
        log_info "Building DEB package..."
        "$SCRIPT_DIR/build-deb.sh" build || log_warning "DEB build failed"
    else
        log_warning "dpkg-deb not found, skipping DEB package"
    fi

    if [[ "$has_rpm" == "true" ]]; then
        log_info "Building RPM package..."
        "$SCRIPT_DIR/build-rpm.sh" build || log_warning "RPM build failed"
    else
        log_warning "rpmbuild not found, skipping RPM package"
    fi

    if [[ "$has_dpkg" == "false" ]] && [[ "$has_rpm" == "false" ]]; then
        log_error "No package build tools found"
        log_info "Install dpkg-deb (apt install dpkg) or rpmbuild (dnf install rpm-build)"
        exit 1
    fi

    log_success "Package building complete!"
}

show_help() {
    echo "PreOffice Linux Package Builder"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  auto       Auto-detect distro and build appropriate package (default)"
    echo "  all        Build both DEB and RPM packages (if tools available)"
    echo "  deb        Build DEB package only"
    echo "  rpm        Build RPM package only"
    echo "  clean      Clean all build artifacts"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 auto    # Build for current distribution"
    echo "  $0 all     # Build all package types"
    echo "  $0 deb     # Build DEB package"
    echo "  $0 rpm     # Build RPM package"
}

# =============================================================================
# Main
# =============================================================================

case "${1:-auto}" in
    auto)
        build_for_distro "${@:2}"
        ;;
    all)
        build_all
        ;;
    deb)
        "$SCRIPT_DIR/build-deb.sh" "${@:2}"
        ;;
    rpm)
        "$SCRIPT_DIR/build-rpm.sh" "${@:2}"
        ;;
    clean)
        "$SCRIPT_DIR/build-deb.sh" clean
        "$SCRIPT_DIR/build-rpm.sh" clean
        log_success "All build artifacts cleaned"
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
