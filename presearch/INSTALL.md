# PreOffice Installation Guide

This guide covers installing PreOffice customizations on top of an existing LibreOffice installation.

## Prerequisites

- LibreOffice 7.x or later installed
- Python 3.6+ (for Python installer) or Bash (for shell installer)

## Quick Install

### macOS / Linux

```bash
cd presearch
./install.sh
```

Or using Python:
```bash
python3 install.py
```

### Windows

Double-click `install.bat` or run in Command Prompt:
```cmd
install.bat
```

Or using Python:
```cmd
python install.py
```

## Installation Options

### Custom LibreOffice Path

If LibreOffice is installed in a non-standard location:

```bash
# Shell
./install.sh --libreoffice-path /path/to/libreoffice

# Python
python3 install.py --libreoffice-path /path/to/libreoffice
```

### Uninstall

To remove PreOffice customizations:

```bash
# Shell
./install.sh --uninstall

# Python
python3 install.py --uninstall
```

## What Gets Installed

| Component | Location | Description |
|-----------|----------|-------------|
| Color Schemes | `user/registrymodifications/` | Light, Dark, and High Contrast themes |
| Icon Theme | `user/config/images_presearch/` | Modern flat icons with Presearch Blue |
| Dark Icons | `user/config/images_presearch_dark/` | Icons optimized for dark mode |
| Templates | `user/template/PreOffice/` | Writer, Calc, and Impress templates |
| Start Center | `user/config/startcenter/` | Branding and app icons |
| Defaults | `user/registrymodifications/` | Security and auto-save settings |

## Post-Installation Setup

1. **Restart LibreOffice** completely (close all windows)

2. **Enable Icon Theme**:
   - Go to `Tools > Options > View`
   - Under "Icon Theme", select "Presearch"
   - Click OK

3. **Enable Dark Mode** (optional):
   - Go to `Tools > Options > Application Colors`
   - Select "PreOffice Dark" from the scheme dropdown

4. **Access Templates**:
   - Go to `File > New > Templates`
   - Navigate to the "PreOffice" folder

## Troubleshooting

### Icons Not Appearing

1. Close all LibreOffice windows
2. Delete the cache:
   - macOS: `~/Library/Application Support/LibreOffice/4/user/cache`
   - Linux: `~/.config/libreoffice/4/user/cache`
   - Windows: `%APPDATA%\LibreOffice\4\user\cache`
3. Restart LibreOffice

### Templates Not Showing

1. Check `Tools > Options > Paths > Templates`
2. Ensure the user template path is included
3. Restart LibreOffice

### Reverting Changes

Run the uninstall command:
```bash
./install.sh --uninstall
```

Then restart LibreOffice. Your original settings will be restored from the backup.

## File Structure

```
presearch/
├── install.sh          # Bash installer (macOS/Linux)
├── install.bat         # Batch installer (Windows)
├── install.py          # Python installer (cross-platform)
├── INSTALL.md          # This file
└── ui/
    ├── color-scheme/   # XCU color configurations
    ├── defaults/       # Default settings
    ├── icon-theme/     # Light mode SVG icons
    ├── icon-theme-dark/# Dark mode SVG icons
    ├── startcenter/    # Start Center branding
    └── templates/      # Document templates
        ├── writer/     # Writer templates (.fodt)
        ├── calc/       # Calc templates (.fods)
        └── impress/    # Impress templates (.fodp)
```

## Support

For issues or questions:
- Check the [PreOffice Repository](https://github.com/presearch/preoffice)
- Open an issue with your OS and LibreOffice version
