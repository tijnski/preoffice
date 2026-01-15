#!/bin/bash
# =============================================================================
# PreOffice macOS DMG Installer Creator
# Creates a distributable .dmg file for macOS
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Configuration
APP_NAME="PreOffice"
APP_VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${APP_VERSION}-macOS"
VOLUME_NAME="${APP_NAME} ${APP_VERSION}"
APP_BUNDLE="${APP_NAME}.app"
BUILD_DIR="${PROJECT_ROOT}/build/macos"
DMG_OUTPUT="${PROJECT_ROOT}/dist/${DMG_NAME}.dmg"

# Size of the DMG (in MB) - LibreOffice is large
DMG_SIZE="2048"

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
# Prerequisites Check
# =============================================================================

check_prerequisites() {
    log_info "Checking prerequisites..."

    # Check for required tools
    local tools=("hdiutil" "codesign" "productbuild")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_warning "$tool not found (optional for advanced features)"
        fi
    done

    # Check if LibreOffice was built
    if [[ ! -d "${PROJECT_ROOT}/instdir" ]]; then
        log_error "LibreOffice build not found at ${PROJECT_ROOT}/instdir"
        log_info "Please build LibreOffice first using: cd ${PROJECT_ROOT} && ./build.sh build"
        exit 1
    fi

    log_success "Prerequisites check complete"
}

# =============================================================================
# Build Functions
# =============================================================================

prepare_app_bundle() {
    log_info "Preparing application bundle..."

    # Clean and create build directory
    rm -rf "${BUILD_DIR}"
    mkdir -p "${BUILD_DIR}"
    mkdir -p "$(dirname "$DMG_OUTPUT")"

    # Copy the built LibreOffice app bundle
    if [[ -d "${PROJECT_ROOT}/instdir/${APP_BUNDLE}" ]]; then
        log_info "Copying application bundle..."
        cp -R "${PROJECT_ROOT}/instdir/${APP_BUNDLE}" "${BUILD_DIR}/"
    elif [[ -d "${PROJECT_ROOT}/instdir/LibreOffice.app" ]]; then
        log_info "Renaming LibreOffice.app to ${APP_BUNDLE}..."
        cp -R "${PROJECT_ROOT}/instdir/LibreOffice.app" "${BUILD_DIR}/${APP_BUNDLE}"
    else
        log_error "Application bundle not found in instdir"
        exit 1
    fi

    # Apply PreOffice customizations
    apply_customizations

    log_success "Application bundle prepared"
}

apply_customizations() {
    log_info "Applying PreOffice customizations..."

    local APP_PATH="${BUILD_DIR}/${APP_BUNDLE}"
    local CONTENTS="${APP_PATH}/Contents"
    local RESOURCES="${CONTENTS}/Resources"
    local SHARE="${CONTENTS}/share"

    # Update Info.plist
    if [[ -f "${CONTENTS}/Info.plist" ]]; then
        log_info "Updating Info.plist..."
        /usr/libexec/PlistBuddy -c "Set :CFBundleName '${APP_NAME}'" "${CONTENTS}/Info.plist" 2>/dev/null || true
        /usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName '${APP_NAME}'" "${CONTENTS}/Info.plist" 2>/dev/null || true
        /usr/libexec/PlistBuddy -c "Set :CFBundleShortVersionString '${APP_VERSION}'" "${CONTENTS}/Info.plist" 2>/dev/null || true
        /usr/libexec/PlistBuddy -c "Set :CFBundleIdentifier 'com.presearch.preoffice'" "${CONTENTS}/Info.plist" 2>/dev/null || true
    fi

    # Copy branding
    if [[ -d "${PROJECT_ROOT}/presearch/branding" ]]; then
        log_info "Copying branding assets..."
        mkdir -p "${SHARE}/gallery"
        cp -R "${PROJECT_ROOT}/presearch/branding/"* "${SHARE}/gallery/" 2>/dev/null || true
    fi

    # Copy icons
    if [[ -d "${PROJECT_ROOT}/presearch/icons" ]]; then
        log_info "Copying custom icons..."
        mkdir -p "${RESOURCES}/icons"
        cp -R "${PROJECT_ROOT}/presearch/icons/"* "${RESOURCES}/icons/" 2>/dev/null || true
    fi

    # Copy color schemes
    if [[ -d "${PROJECT_ROOT}/presearch/colors" ]]; then
        log_info "Copying color schemes..."
        mkdir -p "${SHARE}/config"
        cp -R "${PROJECT_ROOT}/presearch/colors/"* "${SHARE}/config/" 2>/dev/null || true
    fi

    # Copy templates
    if [[ -d "${PROJECT_ROOT}/presearch/templates" ]]; then
        log_info "Copying templates..."
        mkdir -p "${SHARE}/template"
        cp -R "${PROJECT_ROOT}/presearch/templates/"* "${SHARE}/template/" 2>/dev/null || true
    fi

    # Install PrePanda extension
    if [[ -f "${PROJECT_ROOT}/presearch/extension/PreOffice-1.0.0.oxt" ]]; then
        log_info "Installing PrePanda extension..."
        mkdir -p "${SHARE}/extensions"
        cp "${PROJECT_ROOT}/presearch/extension/PreOffice-1.0.0.oxt" "${SHARE}/extensions/"
    fi

    # Copy Notebookbar customization
    if [[ -d "${PROJECT_ROOT}/presearch/ui/notebookbar" ]]; then
        log_info "Copying Notebookbar customization..."
        mkdir -p "${SHARE}/config/soffice.cfg/ui"
        cp -R "${PROJECT_ROOT}/presearch/ui/notebookbar/"* "${SHARE}/config/soffice.cfg/ui/" 2>/dev/null || true
    fi

    log_success "Customizations applied"
}

sign_app() {
    log_info "Signing application..."

    # Check for signing identity
    SIGNING_IDENTITY="${APPLE_SIGNING_IDENTITY:-}"

    if [[ -z "$SIGNING_IDENTITY" ]]; then
        log_warning "No signing identity found (set APPLE_SIGNING_IDENTITY env var)"
        log_warning "Skipping code signing - app will show as 'unidentified developer'"
        return 0
    fi

    local APP_PATH="${BUILD_DIR}/${APP_BUNDLE}"

    # Sign all frameworks and dylibs first
    find "${APP_PATH}" -type f \( -name "*.dylib" -o -name "*.framework" \) | while read -r file; do
        codesign --force --deep --sign "$SIGNING_IDENTITY" "$file" 2>/dev/null || true
    done

    # Sign the main app
    codesign --force --deep --sign "$SIGNING_IDENTITY" \
        --options runtime \
        --entitlements "${SCRIPT_DIR}/entitlements.plist" \
        "${APP_PATH}"

    # Verify signature
    codesign --verify --deep --strict "${APP_PATH}"

    log_success "Application signed successfully"
}

create_dmg() {
    log_info "Creating DMG installer..."

    # Remove existing DMG
    rm -f "${DMG_OUTPUT}"
    rm -f "${DMG_OUTPUT%.dmg}-temp.dmg"

    # Create temporary DMG
    log_info "Creating temporary DMG..."
    hdiutil create -srcfolder "${BUILD_DIR}" \
        -volname "${VOLUME_NAME}" \
        -fs HFS+ \
        -fsargs "-c c=64,a=16,e=16" \
        -format UDRW \
        -size ${DMG_SIZE}m \
        "${DMG_OUTPUT%.dmg}-temp.dmg"

    # Mount temporary DMG
    log_info "Mounting temporary DMG..."
    local DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "${DMG_OUTPUT%.dmg}-temp.dmg" | \
        egrep '^/dev/' | sed 1q | awk '{print $1}')
    local MOUNT_POINT="/Volumes/${VOLUME_NAME}"

    sleep 2

    # Create symlink to Applications
    log_info "Creating Applications symlink..."
    ln -sf /Applications "${MOUNT_POINT}/Applications"

    # Set window appearance (if SetFile is available)
    if command -v SetFile &> /dev/null; then
        SetFile -a C "${MOUNT_POINT}" 2>/dev/null || true
    fi

    # Create .DS_Store for nice DMG appearance
    create_ds_store "${MOUNT_POINT}"

    # Set custom background (if available)
    if [[ -f "${SCRIPT_DIR}/dmg-background.png" ]]; then
        mkdir -p "${MOUNT_POINT}/.background"
        cp "${SCRIPT_DIR}/dmg-background.png" "${MOUNT_POINT}/.background/background.png"
    fi

    # Unmount
    log_info "Finalizing DMG..."
    sync
    hdiutil detach "${DEVICE}"

    # Convert to compressed read-only DMG
    log_info "Compressing DMG..."
    hdiutil convert "${DMG_OUTPUT%.dmg}-temp.dmg" \
        -format UDZO \
        -imagekey zlib-level=9 \
        -o "${DMG_OUTPUT}"

    # Remove temporary DMG
    rm -f "${DMG_OUTPUT%.dmg}-temp.dmg"

    log_success "DMG created: ${DMG_OUTPUT}"
    log_info "Size: $(du -h "${DMG_OUTPUT}" | cut -f1)"
}

create_ds_store() {
    local MOUNT_POINT="$1"

    # Create a simple AppleScript to set DMG window appearance
    osascript <<EOF
tell application "Finder"
    tell disk "${VOLUME_NAME}"
        open
        set current view of container window to icon view
        set toolbar visible of container window to false
        set statusbar visible of container window to false
        set the bounds of container window to {400, 100, 920, 440}
        set theViewOptions to the icon view options of container window
        set arrangement of theViewOptions to not arranged
        set icon size of theViewOptions to 128
        set position of item "${APP_BUNDLE}" of container window to {150, 170}
        set position of item "Applications" of container window to {370, 170}
        update without registering applications
        close
    end tell
end tell
EOF
}

notarize_dmg() {
    log_info "Notarizing DMG..."

    # Check for notarization credentials
    if [[ -z "${APPLE_ID}" ]] || [[ -z "${APPLE_APP_PASSWORD}" ]] || [[ -z "${APPLE_TEAM_ID}" ]]; then
        log_warning "Notarization credentials not found"
        log_warning "Set APPLE_ID, APPLE_APP_PASSWORD, and APPLE_TEAM_ID env vars"
        log_warning "Skipping notarization"
        return 0
    fi

    # Submit for notarization
    xcrun notarytool submit "${DMG_OUTPUT}" \
        --apple-id "${APPLE_ID}" \
        --password "${APPLE_APP_PASSWORD}" \
        --team-id "${APPLE_TEAM_ID}" \
        --wait

    # Staple the notarization ticket
    xcrun stapler staple "${DMG_OUTPUT}"

    log_success "DMG notarized successfully"
}

# =============================================================================
# Create Supporting Files
# =============================================================================

create_entitlements() {
    log_info "Creating entitlements file..."

    cat > "${SCRIPT_DIR}/entitlements.plist" << 'ENTITLEMENTS'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
    <key>com.apple.security.cs.disable-library-validation</key>
    <true/>
    <key>com.apple.security.automation.apple-events</key>
    <true/>
    <key>com.apple.security.files.user-selected.read-write</key>
    <true/>
    <key>com.apple.security.network.client</key>
    <true/>
    <key>com.apple.security.print</key>
    <true/>
</dict>
</plist>
ENTITLEMENTS

    log_success "Entitlements file created"
}

create_background() {
    log_info "Creating DMG background image..."

    # Create a simple background with Python/PIL if available
    if command -v python3 &> /dev/null; then
        python3 << 'PYTHON_SCRIPT'
try:
    from PIL import Image, ImageDraw, ImageFont
    import os

    width, height = 520, 340
    img = Image.new('RGB', (width, height), '#2D8EFF')
    draw = ImageDraw.Draw(img)

    # Add gradient effect
    for y in range(height):
        alpha = int(255 * (1 - y / height * 0.3))
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            factor = 1 - (y / height * 0.3)
            img.putpixel((x, y), (int(r * factor), int(g * factor), int(b * factor)))

    # Add text
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
    except:
        font = ImageFont.load_default()

    text = "Drag PreOffice to Applications"
    draw.text((width//2, height - 40), text, fill='white', font=font, anchor='mm')

    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '.'
    img.save(os.path.join(script_dir, 'dmg-background.png'))
    print("Background image created")
except ImportError:
    print("PIL not available, skipping background creation")
except Exception as e:
    print(f"Could not create background: {e}")
PYTHON_SCRIPT
    else
        log_warning "Python3 not available, skipping background image creation"
    fi
}

# =============================================================================
# Main
# =============================================================================

show_help() {
    echo "PreOffice macOS DMG Installer Creator"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build       Build the DMG installer (default)"
    echo "  sign        Sign the application only"
    echo "  notarize    Notarize the DMG"
    echo "  clean       Remove build artifacts"
    echo "  help        Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  APPLE_SIGNING_IDENTITY  Code signing identity"
    echo "  APPLE_ID               Apple ID for notarization"
    echo "  APPLE_APP_PASSWORD     App-specific password for notarization"
    echo "  APPLE_TEAM_ID          Developer Team ID"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build unsigned DMG"
    echo "  APPLE_SIGNING_IDENTITY='Developer ID' $0 build  # Build signed DMG"
}

main() {
    case "${1:-build}" in
        build)
            check_prerequisites
            create_entitlements
            create_background
            prepare_app_bundle
            sign_app
            create_dmg
            ;;
        sign)
            sign_app
            ;;
        notarize)
            notarize_dmg
            ;;
        clean)
            log_info "Cleaning build artifacts..."
            rm -rf "${BUILD_DIR}"
            rm -f "${DMG_OUTPUT}"
            rm -f "${SCRIPT_DIR}/entitlements.plist"
            rm -f "${SCRIPT_DIR}/dmg-background.png"
            log_success "Clean complete"
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
}

main "$@"
