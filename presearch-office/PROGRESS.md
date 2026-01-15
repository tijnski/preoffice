# PreOffice - Presearch Office Edition

## Current Progress Report

**Date:** January 10, 2026

---

## Overview

PreOffice is a no-fork skin + extension layer on top of LibreOffice, branded with Presearch colors and integrated Presearch services.

---

## What's Been Created

### 1. Repository Structure ✅
```
presearch-office/
├── CLAUDE.md                    # AI instructions
├── brand/
│   ├── tokens.json              # Brand colors/tokens
│   ├── tokens.css               # CSS variables
│   ├── tokens.scss              # SCSS variables
│   ├── README.md
│   └── assets/logos/            # Presearch logo SVGs
├── icon-theme/
│   ├── src-svg/                 # Source icons
│   ├── dist/images_presearch.zip
│   ├── tools/build.sh
│   └── README.md
├── extension/
│   ├── src/
│   │   ├── python/PresearchTools.py
│   │   ├── Addons.xcu
│   │   ├── description.xml
│   │   └── META-INF/manifest.xml
│   ├── dist/presearch-tools-1.0.0.oxt
│   └── build.sh
├── installer/
│   ├── macos/install.sh
│   ├── windows/install.ps1
│   └── linux/install.sh
└── .github/workflows/build.yml
```

### 2. Brand Tokens ✅
- **Primary:** `#2D8EFF` (Presearch Blue)
- **Text Primary:** `#000000`
- **Text Secondary:** `#494949`
- **Background Tint:** `#EAF3FF`
- **Background Soft:** `#FAFBFC`
- Dark mode and high contrast variants included

### 3. Icon Theme ✅ (Fixed structure)
- 5 custom SVG icons created with Presearch branding
- Uses actual Presearch logo for start center
- Built as `images_presearch.zip` with correct LibreOffice structure
- Icons: `lc_newdoc.svg`, `lc_open.svg`, `lc_save.svg`, `lc_searchdialog.svg`
- **Note:** Custom themes require LibreOffice configuration to appear in settings

### 4. Extension ✅ (Fixed, ready for testing)
- Menu "PreOffice" appears in LibreOffice
- 4 commands defined:
  - Search with Presearch
  - Ask PreGPT
  - Privacy Check
  - Export to PreStorage
- **Fixed:** Script path changed from `location=user:uno_packages/com.presearch.tools` to `location=user:uno_packages`
- **Fixed:** Removed non-existent `PresearchTools.xcu` reference from manifest

### 5. Installers ✅
- macOS, Windows, Linux scripts created
- Download LibreOffice + install extension + theme

### 6. CI/CD ✅
- GitHub Actions workflow for building all artifacts

---

## Current Issues

### Issue 1: Extension Scripts - FIXED ✅
**Previous Error:**
```
KeyError: 'PresearchTools.py$SearchWithPresearc'
```

**Fix Applied:**
- Changed script path from `location=user:uno_packages/com.presearch.tools` to `location=user:uno_packages`
- Removed reference to non-existent `PresearchTools.xcu` from manifest.xml
- Extension rebuilt and reinstalled

**Status:** Ready for testing - restart LibreOffice and try the PreOffice menu commands

### Issue 2: Icon Theme Registration
**Status:** Structure fixed, but custom themes need LibreOffice configuration

**What was fixed:**
- Removed `presearch/` subdirectory wrapper - icons now at root level
- Renamed `lc_new.svg` to `lc_newdoc.svg` to match LibreOffice conventions
- Theme structure now matches `images_colibre_svg.zip`

**Remaining work:**
- LibreOffice doesn't automatically discover custom themes in user config
- Need to either override an existing theme or register via configuration

---

## LibreOffice Build Status

**Status:** 🔄 Still building in background

**Build ID:** b871aa7

**Monitor with:**
```bash
tail -f /var/folders/5k/tcq0rss15y14cfcmtp2bqhm80000gn/T/claude/-Users-tijnhoorneman-Documents-Documents-MacBook-presearch-preoffice/tasks/b871aa7.output
```

---

## Files Ready to Use

| File | Location | Status |
|------|----------|--------|
| Extension .oxt | `extension/dist/presearch-tools-1.0.0.oxt` | Built (script issue) |
| Icon Theme | `icon-theme/dist/images_presearch.zip` | Built (not loading) |
| Brand Tokens | `brand/tokens.json` | Ready |
| Presearch Logos | `brand/assets/logos/*.svg` | Ready |
| macOS Installer | `installer/macos/install.sh` | Ready |

---

## To Fix Extension

The extension script path needs to match LibreOffice's expectations. Try:

1. Check where extension is installed:
```bash
ls -la "$HOME/Library/Application Support/LibreOffice/4/user/uno_packages/cache/uno_packages/"
```

2. Update `Addons.xcu` with correct path format

3. Rebuild and reinstall:
```bash
cd extension && ./build.sh
unopkg remove com.presearch.tools
unopkg add dist/presearch-tools-1.0.0.oxt
```

---

## To Fix Icon Theme

1. Check LibreOffice icon theme structure:
```bash
unzip -l /Applications/LibreOffice.app/Contents/Resources/config/images_colibre.zip | head -30
```

2. Match the same structure in our theme

3. Copy to correct location:
```bash
cp icon-theme/dist/images_presearch.zip "$HOME/Library/Application Support/LibreOffice/4/user/config/"
```

---

## Brand Colors Reference

```css
--pre-primary: #2D8EFF;
--pre-text-primary: #000000;
--pre-text-secondary: #494949;
--pre-bg-tint: #EAF3FF;
--pre-bg-soft: #FAFBFC;
--pre-bg-base: #FFFFFF;
```

---

## Next Steps

1. [x] Fix extension Python script path
2. [x] Fix icon theme structure
3. [ ] Test all 4 extension commands (restart LibreOffice first!)
4. [ ] Register icon theme in LibreOffice configuration
5. [ ] Add more icons (Writer, Calc, Impress app icons)
6. [ ] Create splash screen with Presearch branding

## Testing the Extension

1. Restart LibreOffice completely (quit all windows)
2. Open any document (Writer, Calc, or Impress)
3. Look for "PreOffice" menu in the menu bar
4. Test each command:
   - **Search with Presearch:** Select text, click menu item → should open browser
   - **Ask PreGPT:** Select text, click menu item → should open PreGPT
   - **Privacy Check:** Click menu item → should show metadata report
   - **Export to PreStorage:** Click menu item → should show instructions
