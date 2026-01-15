#!/bin/bash
#
# PreOffice Customization Installer
# Applies PreOffice UI customizations to LibreOffice
#
# Usage: ./install.sh [--uninstall] [--libreoffice-path <path>]
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UI_DIR="$SCRIPT_DIR/ui"
AI_DIR="$SCRIPT_DIR/ai-assistant"

# Default paths
LIBREOFFICE_PATH=""
USER_PROFILE=""
UNINSTALL=false

# Print colored output
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Detect OS and LibreOffice paths
detect_paths() {
    case "$(uname -s)" in
        Darwin)
            # macOS
            if [[ -z "$LIBREOFFICE_PATH" ]]; then
                if [[ -d "/Applications/LibreOffice.app" ]]; then
                    LIBREOFFICE_PATH="/Applications/LibreOffice.app/Contents"
                elif [[ -d "$HOME/Applications/LibreOffice.app" ]]; then
                    LIBREOFFICE_PATH="$HOME/Applications/LibreOffice.app/Contents"
                fi
            fi
            USER_PROFILE="$HOME/Library/Application Support/LibreOffice/4/user"
            ;;
        Linux)
            # Linux
            if [[ -z "$LIBREOFFICE_PATH" ]]; then
                if [[ -d "/usr/lib/libreoffice" ]]; then
                    LIBREOFFICE_PATH="/usr/lib/libreoffice"
                elif [[ -d "/opt/libreoffice" ]]; then
                    LIBREOFFICE_PATH="/opt/libreoffice"
                elif [[ -d "/usr/lib64/libreoffice" ]]; then
                    LIBREOFFICE_PATH="/usr/lib64/libreoffice"
                fi
            fi
            USER_PROFILE="$HOME/.config/libreoffice/4/user"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            # Windows
            if [[ -z "$LIBREOFFICE_PATH" ]]; then
                if [[ -d "/c/Program Files/LibreOffice" ]]; then
                    LIBREOFFICE_PATH="/c/Program Files/LibreOffice"
                elif [[ -d "/c/Program Files (x86)/LibreOffice" ]]; then
                    LIBREOFFICE_PATH="/c/Program Files (x86)/LibreOffice"
                fi
            fi
            USER_PROFILE="$APPDATA/LibreOffice/4/user"
            ;;
        *)
            error "Unsupported operating system: $(uname -s)"
            ;;
    esac
}

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --uninstall)
                UNINSTALL=true
                shift
                ;;
            --libreoffice-path)
                LIBREOFFICE_PATH="$2"
                shift 2
                ;;
            --help|-h)
                echo "PreOffice Customization Installer"
                echo ""
                echo "Usage: $0 [OPTIONS]"
                echo ""
                echo "Options:"
                echo "  --libreoffice-path <path>  Specify LibreOffice installation path"
                echo "  --uninstall                Remove PreOffice customizations"
                echo "  --help, -h                 Show this help message"
                echo ""
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                ;;
        esac
    done
}

# Verify paths exist
verify_paths() {
    if [[ -z "$LIBREOFFICE_PATH" ]] || [[ ! -d "$LIBREOFFICE_PATH" ]]; then
        error "LibreOffice installation not found. Use --libreoffice-path to specify."
    fi

    info "LibreOffice found at: $LIBREOFFICE_PATH"
    info "User profile at: $USER_PROFILE"
}

# Create backup of existing files
create_backup() {
    local backup_dir="$USER_PROFILE/preoffice_backup_$(date +%Y%m%d_%H%M%S)"

    if [[ -d "$USER_PROFILE/registrymodifications.xcu" ]]; then
        mkdir -p "$backup_dir"
        cp -r "$USER_PROFILE/registrymodifications.xcu" "$backup_dir/" 2>/dev/null || true
        info "Backup created at: $backup_dir"
    fi
}

# Install color schemes
install_color_schemes() {
    info "Installing color schemes..."

    local target_dir="$USER_PROFILE/registrymodifications"
    mkdir -p "$target_dir"

    # Copy XCU files
    for xcu in "$UI_DIR/color-scheme/"*.xcu; do
        if [[ -f "$xcu" ]]; then
            cp "$xcu" "$target_dir/"
            success "Installed: $(basename "$xcu")"
        fi
    done
}

# Install icon theme
install_icons() {
    info "Installing icon theme..."

    # User icon theme directory
    local icon_dir="$USER_PROFILE/config/images_presearch"
    mkdir -p "$icon_dir/cmd"

    # Copy light theme icons
    if [[ -d "$UI_DIR/icon-theme/cmd" ]]; then
        cp "$UI_DIR/icon-theme/cmd/"*.svg "$icon_dir/cmd/" 2>/dev/null || true
        success "Installed light theme icons"
    fi

    # Copy links.txt if exists
    if [[ -f "$UI_DIR/icon-theme/links.txt" ]]; then
        cp "$UI_DIR/icon-theme/links.txt" "$icon_dir/"
    fi

    # Install dark theme icons
    local dark_icon_dir="$USER_PROFILE/config/images_presearch_dark"
    mkdir -p "$dark_icon_dir/cmd"

    if [[ -d "$UI_DIR/icon-theme-dark/cmd" ]]; then
        cp "$UI_DIR/icon-theme-dark/cmd/"*.svg "$dark_icon_dir/cmd/" 2>/dev/null || true
        success "Installed dark theme icons"
    fi

    # Create icon theme zip for system-wide installation (optional)
    if [[ -f "$UI_DIR/icon-theme/dist/images_presearch.zip" ]]; then
        local system_icons
        case "$(uname -s)" in
            Darwin)
                system_icons="$LIBREOFFICE_PATH/Resources/share/config"
                ;;
            *)
                system_icons="$LIBREOFFICE_PATH/share/config"
                ;;
        esac

        if [[ -d "$system_icons" ]] && [[ -w "$system_icons" ]]; then
            cp "$UI_DIR/icon-theme/dist/images_presearch.zip" "$system_icons/"
            success "Installed system icon theme"
        else
            warn "Cannot write to system icon directory (requires sudo)"
        fi
    fi
}

# Install templates
install_templates() {
    info "Installing templates..."

    local template_dir="$USER_PROFILE/template"
    mkdir -p "$template_dir/PreOffice"

    # Copy Writer templates
    if [[ -d "$UI_DIR/templates/writer" ]]; then
        mkdir -p "$template_dir/PreOffice/Writer"
        cp "$UI_DIR/templates/writer/"*.fodt "$template_dir/PreOffice/Writer/" 2>/dev/null || true
        success "Installed Writer templates"
    fi

    # Copy Calc templates
    if [[ -d "$UI_DIR/templates/calc" ]]; then
        mkdir -p "$template_dir/PreOffice/Calc"
        cp "$UI_DIR/templates/calc/"*.fods "$template_dir/PreOffice/Calc/" 2>/dev/null || true
        success "Installed Calc templates"
    fi

    # Copy Impress templates
    if [[ -d "$UI_DIR/templates/impress" ]]; then
        mkdir -p "$template_dir/PreOffice/Impress"
        cp "$UI_DIR/templates/impress/"*.fodp "$template_dir/PreOffice/Impress/" 2>/dev/null || true
        success "Installed Impress templates"
    fi
}

# Install Start Center customizations
install_startcenter() {
    info "Installing Start Center branding..."

    local startcenter_dir="$USER_PROFILE/config/startcenter"
    mkdir -p "$startcenter_dir"

    if [[ -d "$UI_DIR/startcenter" ]]; then
        # Copy SVG assets
        cp "$UI_DIR/startcenter/"*.svg "$startcenter_dir/" 2>/dev/null || true

        # Copy XCU configs
        cp "$UI_DIR/startcenter/"*.xcu "$startcenter_dir/" 2>/dev/null || true

        success "Installed Start Center branding"
    fi
}

# Install default settings
install_defaults() {
    info "Installing default settings..."

    local config_dir="$USER_PROFILE/registrymodifications"
    mkdir -p "$config_dir"

    if [[ -d "$UI_DIR/defaults" ]]; then
        cp "$UI_DIR/defaults/"*.xcu "$config_dir/" 2>/dev/null || true
        success "Installed default settings"
    fi
}

# Install PrePanda AI Assistant
install_ai_assistant() {
    info "Installing PrePanda AI Assistant..."

    local ai_install_dir="$USER_PROFILE/Scripts/python"
    mkdir -p "$ai_install_dir"

    # Copy Python service files
    if [[ -d "$AI_DIR/python" ]]; then
        cp "$AI_DIR/python/"*.py "$ai_install_dir/" 2>/dev/null || true
        success "Installed AI Python modules"
    fi

    # Copy config
    local config_dir="$USER_PROFILE/config/prepanda"
    mkdir -p "$config_dir"

    if [[ -f "$AI_DIR/config/prepanda.json" ]]; then
        cp "$AI_DIR/config/prepanda.json" "$config_dir/"
        success "Installed AI configuration"
    fi

    # Copy web assets (CSS, JS, HTML)
    local assets_dir="$USER_PROFILE/config/prepanda/assets"
    mkdir -p "$assets_dir/css" "$assets_dir/js"

    if [[ -d "$AI_DIR/css" ]]; then
        cp "$AI_DIR/css/"*.css "$assets_dir/css/" 2>/dev/null || true
    fi

    if [[ -d "$AI_DIR/js" ]]; then
        cp "$AI_DIR/js/"*.js "$assets_dir/js/" 2>/dev/null || true
    fi

    if [[ -f "$AI_DIR/prepanda-panel.html" ]]; then
        cp "$AI_DIR/prepanda-panel.html" "$assets_dir/"
    fi

    success "Installed PrePanda AI Assistant"

    # Check for API key
    if [[ -z "${VENICE_API_KEY:-}" ]]; then
        warn "VENICE_API_KEY not set. Set it to enable AI features:"
        echo "    export VENICE_API_KEY='your-api-key'"
    fi
}

# Apply registry modifications
apply_registry() {
    info "Applying registry modifications..."

    local reg_file="$USER_PROFILE/registrymodifications.xcu"

    # Create registry file if it doesn't exist
    if [[ ! -f "$reg_file" ]]; then
        cat > "$reg_file" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
</oor:items>
EOF
    fi

    # Add PreOffice settings
    # Note: This is a simplified approach. Full integration requires modifying the XML properly.

    local temp_file=$(mktemp)

    # Check if PreOffice settings already exist
    if ! grep -q "PreOffice" "$reg_file" 2>/dev/null; then
        # Insert settings before closing tag
        sed '/<\/oor:items>/d' "$reg_file" > "$temp_file"

        cat >> "$temp_file" << 'EOF'

<!-- PreOffice Customizations -->
<item oor:path="/org.openoffice.Office.Common/Misc">
  <prop oor:name="FirstRun" oor:op="fuse"><value>false</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Misc">
  <prop oor:name="ShowTipOfTheDay" oor:op="fuse"><value>false</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Save/Document">
  <prop oor:name="AutoSave" oor:op="fuse"><value>true</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Save/Document">
  <prop oor:name="AutoSaveTimeIntervall" oor:op="fuse"><value>5</value></prop>
</item>
<item oor:path="/org.openoffice.Office.Common/Security/Scripting">
  <prop oor:name="MacroSecurityLevel" oor:op="fuse"><value>2</value></prop>
</item>

</oor:items>
EOF

        mv "$temp_file" "$reg_file"
        success "Applied registry modifications"
    else
        info "PreOffice settings already present in registry"
    fi
}

# Uninstall PreOffice customizations
uninstall() {
    info "Uninstalling PreOffice customizations..."

    # Remove icon themes
    rm -rf "$USER_PROFILE/config/images_presearch" 2>/dev/null || true
    rm -rf "$USER_PROFILE/config/images_presearch_dark" 2>/dev/null || true

    # Remove templates
    rm -rf "$USER_PROFILE/template/PreOffice" 2>/dev/null || true

    # Remove Start Center customizations
    rm -rf "$USER_PROFILE/config/startcenter" 2>/dev/null || true

    # Remove AI Assistant
    rm -rf "$USER_PROFILE/config/prepanda" 2>/dev/null || true
    rm -f "$USER_PROFILE/Scripts/python/prepanda_"*.py 2>/dev/null || true

    # Remove registry modifications directory
    rm -rf "$USER_PROFILE/registrymodifications" 2>/dev/null || true

    # Note: We don't modify registrymodifications.xcu to avoid breaking other settings
    warn "Registry modifications not removed (manual cleanup may be needed)"

    success "PreOffice customizations removed"
}

# Main installation
install() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     PreOffice Customization Installer      ║${NC}"
    echo -e "${BLUE}║        Part of the Pre-suite               ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
    echo ""

    # Create user profile directory if needed
    mkdir -p "$USER_PROFILE"

    # Create backup
    create_backup

    # Install components
    install_color_schemes
    install_icons
    install_templates
    install_ai_assistant
    install_startcenter
    install_defaults
    apply_registry

    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║     Installation Complete!                 ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Restart LibreOffice"
    echo "  2. Go to Tools > Options > View"
    echo "  3. Select 'Presearch' icon theme"
    echo "  4. Access templates via File > New > Templates"
    echo ""
    echo "PrePanda AI Assistant:"
    echo "  - Set VENICE_API_KEY environment variable for AI features"
    echo "  - Access via Tools > PrePanda or right-click context menu"
    echo ""
}

# Entry point
main() {
    parse_args "$@"
    detect_paths
    verify_paths

    if [[ "$UNINSTALL" == true ]]; then
        uninstall
    else
        install
    fi
}

main "$@"
