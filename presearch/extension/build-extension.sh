#!/bin/bash
# =============================================================================
# PreOffice Extension Build Script
# Builds the PrePanda AI extension as an .oxt package
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
EXTENSION_NAME="PreOffice"
EXTENSION_VERSION="1.0.0"
OUTPUT_FILE="${EXTENSION_NAME}-${EXTENSION_VERSION}.oxt"

# Colors for output
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
# Build Functions
# =============================================================================

clean() {
    log_info "Cleaning previous builds..."
    rm -f "$OUTPUT_FILE"
    rm -rf build/
    log_success "Clean complete"
}

validate() {
    log_info "Validating extension structure..."

    local required_files=(
        "META-INF/manifest.xml"
        "description.xml"
        "Addons.xcu"
        "OptionsDialog.xcu"
        "python/prepanda.py"
        "license/MIT.txt"
        "description/description_en.txt"
    )

    local missing=0
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Missing required file: $file"
            missing=1
        fi
    done

    if [[ $missing -eq 1 ]]; then
        log_error "Validation failed - missing required files"
        exit 1
    fi

    log_success "All required files present"
}

convert_icons() {
    log_info "Converting SVG icons to PNG..."

    # Check if we have rsvg-convert or inkscape
    if command -v rsvg-convert &> /dev/null; then
        CONVERTER="rsvg-convert"
    elif command -v inkscape &> /dev/null; then
        CONVERTER="inkscape"
    else
        log_warning "No SVG converter found (rsvg-convert or inkscape)"
        log_warning "Using SVG icons directly - PNG conversion skipped"
        return 0
    fi

    mkdir -p icons

    if [[ "$CONVERTER" == "rsvg-convert" ]]; then
        if [[ -f "icons/preoffice_128.png.svg" ]]; then
            rsvg-convert -w 128 -h 128 icons/preoffice_128.png.svg > icons/preoffice_128.png
            log_success "Created preoffice_128.png"
        fi
        if [[ -f "icons/prepanda_22.svg" ]]; then
            rsvg-convert -w 22 -h 22 icons/prepanda_22.svg > icons/prepanda_22.png
            log_success "Created prepanda_22.png"
        fi
    elif [[ "$CONVERTER" == "inkscape" ]]; then
        if [[ -f "icons/preoffice_128.png.svg" ]]; then
            inkscape icons/preoffice_128.png.svg --export-type=png --export-filename=icons/preoffice_128.png -w 128 -h 128
            log_success "Created preoffice_128.png"
        fi
        if [[ -f "icons/prepanda_22.svg" ]]; then
            inkscape icons/prepanda_22.svg --export-type=png --export-filename=icons/prepanda_22.png -w 22 -h 22
            log_success "Created prepanda_22.png"
        fi
    fi

    log_success "Icon conversion complete"
}

build() {
    log_info "Building extension package: $OUTPUT_FILE"

    # Create build directory
    mkdir -p build

    # Copy all required files
    log_info "Copying extension files..."

    # Core files
    cp description.xml build/
    cp Addons.xcu build/
    cp OptionsDialog.xcu build/

    # Manifest
    mkdir -p build/META-INF
    cp META-INF/manifest.xml build/META-INF/

    # Python scripts
    mkdir -p build/python
    cp python/*.py build/python/

    # Dialogs
    mkdir -p build/dialogs
    cp dialogs/*.xdl build/dialogs/ 2>/dev/null || log_warning "No dialog files found"

    # License
    mkdir -p build/license
    cp license/*.txt build/license/

    # Description
    mkdir -p build/description
    cp description/*.txt build/description/

    # Icons (copy both SVG and PNG if available)
    mkdir -p build/icons
    cp icons/*.svg build/icons/ 2>/dev/null || true
    cp icons/*.png build/icons/ 2>/dev/null || true

    # Create the .oxt file (ZIP format)
    log_info "Creating OXT package..."
    cd build
    zip -r "../$OUTPUT_FILE" . -x "*.DS_Store" -x "*__pycache__*"
    cd ..

    # Verify the package
    log_info "Verifying package contents..."
    unzip -l "$OUTPUT_FILE"

    log_success "Extension built successfully: $OUTPUT_FILE"
    log_info "File size: $(du -h "$OUTPUT_FILE" | cut -f1)"
}

install() {
    log_info "Installing extension..."

    # Find LibreOffice
    if [[ "$OSTYPE" == "darwin"* ]]; then
        UNOPKG="/Applications/LibreOffice.app/Contents/MacOS/unopkg"
        if [[ ! -f "$UNOPKG" ]]; then
            UNOPKG="/Applications/PreOffice.app/Contents/MacOS/unopkg"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        UNOPKG="/usr/bin/unopkg"
        if [[ ! -f "$UNOPKG" ]]; then
            UNOPKG="/opt/libreoffice/program/unopkg"
        fi
    else
        log_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi

    if [[ ! -f "$UNOPKG" ]]; then
        log_error "unopkg not found at: $UNOPKG"
        log_info "Please install the extension manually via Tools > Extension Manager"
        exit 1
    fi

    # Remove old version if exists
    log_info "Removing old version (if exists)..."
    "$UNOPKG" remove com.presearch.preoffice 2>/dev/null || true

    # Install new version
    log_info "Installing new version..."
    "$UNOPKG" add --shared "$OUTPUT_FILE"

    log_success "Extension installed successfully"
    log_info "Restart LibreOffice/PreOffice to activate the extension"
}

uninstall() {
    log_info "Uninstalling extension..."

    # Find LibreOffice
    if [[ "$OSTYPE" == "darwin"* ]]; then
        UNOPKG="/Applications/LibreOffice.app/Contents/MacOS/unopkg"
        if [[ ! -f "$UNOPKG" ]]; then
            UNOPKG="/Applications/PreOffice.app/Contents/MacOS/unopkg"
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        UNOPKG="/usr/bin/unopkg"
    fi

    if [[ -f "$UNOPKG" ]]; then
        "$UNOPKG" remove com.presearch.preoffice
        log_success "Extension uninstalled"
    else
        log_error "unopkg not found"
        exit 1
    fi
}

show_help() {
    echo "PreOffice Extension Build Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build      Build the .oxt extension package (default)"
    echo "  clean      Remove build artifacts"
    echo "  install    Install the extension to LibreOffice/PreOffice"
    echo "  uninstall  Remove the extension"
    echo "  validate   Check extension structure"
    echo "  icons      Convert SVG icons to PNG"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build      # Build the extension"
    echo "  $0 install    # Build and install"
}

# =============================================================================
# Main
# =============================================================================

case "${1:-build}" in
    build)
        clean
        validate
        convert_icons
        build
        ;;
    clean)
        clean
        ;;
    install)
        if [[ ! -f "$OUTPUT_FILE" ]]; then
            clean
            validate
            convert_icons
            build
        fi
        install
        ;;
    uninstall)
        uninstall
        ;;
    validate)
        validate
        ;;
    icons)
        convert_icons
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
