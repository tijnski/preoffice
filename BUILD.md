# PreOffice Build Guide

Complete guide to building PreOffice from source and creating distribution packages.

## Overview

PreOffice is a customized LibreOffice distribution with:
- **PrePanda AI Assistant** - Integrated AI powered by Venice.ai
- **Custom Notebookbar/Ribbon UI** - Modern tabbed interface
- **Presearch Branding** - Custom splash screens, icons, and color schemes
- **Templates** - Document, spreadsheet, and presentation templates

## Prerequisites

### All Platforms
- Git
- Python 3.8+
- At least 16GB RAM (32GB recommended)
- 80GB free disk space

### macOS
```bash
# Install Xcode Command Line Tools
xcode-select --install

# Install dependencies via Homebrew
brew install autoconf automake ccache pkg-config \
    gettext gperf bison flex cppunit boost \
    icu4c nss openssl jpeg libpng tiff
```

### Linux (Debian/Ubuntu)
```bash
sudo apt update
sudo apt install build-essential git autoconf automake \
    ccache flex bison gperf libx11-dev libxext-dev \
    libxrandr-dev libxinerama-dev libfreetype6-dev \
    libfontconfig1-dev libcups2-dev libgtk-3-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libicu-dev libnss3-dev libpng-dev libjpeg-dev \
    libtiff-dev libboost-dev
```

### Linux (Fedora/RHEL)
```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install git autoconf automake ccache flex bison gperf \
    libX11-devel libXext-devel libXrandr-devel libXinerama-devel \
    freetype-devel fontconfig-devel cups-devel gtk3-devel \
    gstreamer1-devel gstreamer1-plugins-base-devel \
    libicu-devel nss-devel libpng-devel libjpeg-devel \
    libtiff-devel boost-devel
```

### Windows
- Visual Studio 2019 or 2022 with C++ workload
- Cygwin with development packages
- WiX Toolset 3.11+ for MSI creation

## Building

### Step 1: Clone and Configure

```bash
# Clone LibreOffice core
git clone https://git.libreoffice.org/core preoffice
cd preoffice

# Copy PreOffice customizations
cp -R /path/to/presearch .

# Configure the build
./autogen.sh --with-vendor="Presearch" \
              --with-product-name="PreOffice" \
              --with-package-version="1.0.0" \
              --enable-release-build
```

Or use the provided configuration:
```bash
cp presearch/autogen.input .
./autogen.sh
```

### Step 2: Build LibreOffice

```bash
# Build (this takes several hours)
make

# Or use the build script
./build.sh build
```

### Step 3: Build the Extension

```bash
cd presearch/extension
./build-extension.sh build
```

This creates `PreOffice-1.0.0.oxt` containing the PrePanda AI extension.

### Step 4: Create Installers

#### macOS (.dmg)
```bash
cd installers/macos
./create-dmg.sh build

# Optional: Sign and notarize
export APPLE_SIGNING_IDENTITY="Developer ID Application: ..."
export APPLE_ID="your@email.com"
export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
export APPLE_TEAM_ID="XXXXXXXXXX"
./create-dmg.sh notarize
```

Output: `dist/PreOffice-1.0.0-macOS.dmg`

#### Windows (.msi)
```powershell
cd installers\windows
.\build-msi.ps1 build
```

Output: `dist\PreOffice-1.0.0-x64.msi`

#### Linux (.deb/.rpm)
```bash
cd installers/linux

# Auto-detect distribution
./build-all.sh auto

# Or build specific package
./build-all.sh deb  # Debian/Ubuntu
./build-all.sh rpm  # Fedora/RHEL
```

Output:
- `dist/preoffice_1.0.0-1_amd64.deb`
- `dist/preoffice-1.0.0-1.x86_64.rpm`

## Project Structure

```
preoffice/
├── autogen.input          # Build configuration
├── build.sh               # Main build script
├── BUILD.md               # This file
├── presearch/
│   ├── branding/          # Splash screens, logos
│   ├── colors/            # Color schemes
│   ├── icons/             # Custom icons
│   ├── templates/         # Document templates
│   ├── start-center/      # Start Center customization
│   ├── ui/
│   │   └── notebookbar/   # Ribbon UI config
│   ├── extension/         # PrePanda extension
│   │   ├── META-INF/
│   │   ├── python/        # Extension code
│   │   ├── dialogs/       # Settings dialogs
│   │   └── build-extension.sh
│   ├── ai-assistant/      # AI assistant components
│   ├── install.sh         # Customization installer
│   └── install.py         # Cross-platform installer
└── installers/
    ├── macos/
    │   └── create-dmg.sh
    ├── windows/
    │   ├── PreOffice.wxs
    │   └── build-msi.ps1
    └── linux/
        ├── build-deb.sh
        ├── build-rpm.sh
        └── build-all.sh
```

## Configuration

### Venice.ai API Key

PrePanda AI requires a Venice.ai API key. Users can configure this:

1. Via PreOffice: Tools > Options > PreOffice > PrePanda AI
2. Via environment: `export VENICE_API_KEY=your-key`
3. Via config file: `~/.config/preoffice/prepanda_config.json`

### Customizing Branding

Edit files in `presearch/branding/`:
- `splash.png` - Startup splash screen
- `intro.png` - Start Center background
- `about.png` - About dialog

### Customizing Colors

Edit files in `presearch/colors/`:
- `preoffice-light.soc` - Light theme palette
- `preoffice-dark.soc` - Dark theme palette
- `preoffice-highcontrast.soc` - Accessibility theme

## Troubleshooting

### Build fails with "out of memory"
- Reduce parallel jobs: `make -j4` instead of `make`
- Add more swap space

### Extension not loading
- Check Python version (3.6+ required)
- Verify extension installed: Tools > Extension Manager
- Check logs: `~/.config/libreoffice/4/user/logs/`

### DMG creation fails on macOS
- Ensure Xcode is installed
- Check permissions on build directories

## Support

- Issues: https://github.com/presearch/preoffice/issues
- Website: https://presearch.com/preoffice
- Email: support@presearch.com
