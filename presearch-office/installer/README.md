# Presearch Office Edition Installers

Platform-specific installers that bundle LibreOffice with Presearch customizations.

## What Gets Installed

1. **LibreOffice** - The official release (downloaded from documentfoundation.org)
2. **Presearch Tools Extension** - Menu/toolbar integration for Presearch services
3. **Presearch Icon Theme** - Custom icons with Presearch branding
4. **Default Configuration** - Optimized settings for Presearch Office Edition

## Installation

### macOS

```bash
cd installer/macos
./install.sh
```

Or right-click and "Open" if you downloaded it.

### Windows

Run PowerShell as Administrator:
```powershell
cd installer\windows
.\install.ps1
```

For silent installation:
```powershell
.\install.ps1 -Silent
```

### Linux

```bash
cd installer/linux
./install.sh
```

Supports: Ubuntu/Debian (apt), Fedora (dnf), Arch (pacman), openSUSE (zypper), and Flatpak.

## Manual Installation

If the automated installer doesn't work for your system:

### 1. Install LibreOffice
Download from: https://www.libreoffice.org/download/download/

### 2. Install Extension
1. Open LibreOffice
2. Go to Tools → Extension Manager
3. Click "Add"
4. Select `extension/dist/presearch-tools.oxt`
5. Restart LibreOffice

### 3. Install Icon Theme
Copy `icon-theme/dist/images_presearch.zip` to:
- **Linux**: `~/.config/libreoffice/4/user/config/`
- **macOS**: `~/Library/Application Support/LibreOffice/4/user/config/`
- **Windows**: `%APPDATA%\LibreOffice\4\user\config\`

### 4. Select Icon Theme
1. Open LibreOffice
2. Go to Tools → Options → View
3. Select "Presearch" from Icon Theme dropdown

## Uninstallation

### Extension
1. Open LibreOffice
2. Go to Tools → Extension Manager
3. Select "Presearch Tools"
4. Click "Remove"

### Icon Theme
Delete `images_presearch.zip` from your user config directory.

### LibreOffice
Use your system's standard uninstall method.

## Troubleshooting

### Extension not loading
- Make sure LibreOffice is completely closed before installing
- Try installing as admin/root
- Check if Python is enabled in LibreOffice

### Icon theme not appearing
- Restart LibreOffice after copying the theme
- Make sure the zip file is in the correct directory
- Check file permissions

### Download fails
- Check your internet connection
- The installer downloads LibreOffice from documentfoundation.org
- Try downloading manually if corporate firewall blocks it

## Building Installers

### Prerequisites
- Built extension (`../extension/dist/presearch-tools.oxt`)
- Built icon theme (`../icon-theme/dist/images_presearch.zip`)

### Build All
```bash
# From repo root
cd extension && ./build.sh
cd ../icon-theme && ./tools/build.sh
```

## Idempotency

All installers are designed to be idempotent - running them multiple times is safe and will not break an existing installation.
