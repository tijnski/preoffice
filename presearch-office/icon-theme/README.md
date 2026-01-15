# Presearch Icon Theme for LibreOffice

A custom icon theme for LibreOffice that uses Presearch brand colors with fallback to Colibre for missing icons.

## Structure

```
icon-theme/
  src-svg/           # Source SVG files (editable)
  build/             # Intermediate build artifacts
  dist/              # Final distributable (images_presearch.zip)
  tools/             # Build scripts
  links.txt          # Fallback mappings to Colibre
  README.md
```

## MVP Icon Set

Priority icons to override (others fall back to Colibre):

### App Icons
- `lc_startcenter.svg` - Start Center icon
- `lc_writerdoc.svg` - Writer document
- `lc_calcdoc.svg` - Calc document
- `lc_impressdoc.svg` - Impress document

### Command Icons
- `cmd/lc_new.svg` - New document
- `cmd/lc_open.svg` - Open document
- `cmd/lc_save.svg` - Save document
- `cmd/lc_exporttopdf.svg` - Export to PDF
- `cmd/lc_undo.svg` - Undo
- `cmd/lc_redo.svg` - Redo
- `cmd/lc_searchdialog.svg` - Search

### File Type Icons
- `res/odt.svg` - OpenDocument Text
- `res/ods.svg` - OpenDocument Spreadsheet
- `res/odp.svg` - OpenDocument Presentation
- `res/pdf.svg` - PDF document

## Design Guidelines

- **Primary color**: `#2D8EFF` (Presearch Blue)
- **Secondary/outline**: `#494949`
- **Background fills**: `#EAF3FF` (light tint)
- **Style**: Flat, clean, minimal
- Use consistent 2px stroke width
- Maintain visual consistency with Colibre's style

## Icon Sizes

LibreOffice uses these standard sizes:
- `lc_` prefix: Large icons (24x24)
- `sc_` prefix: Small icons (16x16)

SVGs should be designed at 24x24 and scaled down for small variants.

## Building

```bash
# Install dependencies
npm install -g svgo

# Build the theme
./tools/build.sh

# Output will be in dist/images_presearch.zip
```

## Installation

### Manual Installation
1. Copy `dist/images_presearch.zip` to:
   - **Linux**: `~/.config/libreoffice/4/user/config/`
   - **macOS**: `~/Library/Application Support/LibreOffice/4/user/config/`
   - **Windows**: `%APPDATA%\LibreOffice\4\user\config\`
2. Restart LibreOffice
3. Go to Tools → Options → View → Icon Theme → Select "Presearch"

### Via Extension
The Presearch Tools extension includes the icon theme and installs it automatically.

## Fallback Mechanism

The `links.txt` file maps missing icons to their Colibre equivalents. This allows us to ship a minimal icon set while maintaining full functionality.

Format:
```
presearch/missing_icon.svg colibre/existing_icon.svg
```

## Development

1. Create/edit SVGs in `src-svg/`
2. Run `./tools/build.sh`
3. Test in LibreOffice
4. Commit changes

### Testing Icons
```bash
# Quick test: copy to user config and restart LO
./tools/install-local.sh
```
