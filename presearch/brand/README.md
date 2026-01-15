# PreOffice Branding

This directory contains branding assets and patches for PreOffice.

## Directory Structure

```
brand/
├── assets/                 # Logos and visual assets
├── patches/                # Git patches for core branding
│   └── 0001-Rebrand-to-PreOffice.patch
├── splash/                 # Splash screen images
├── tokens.json             # Brand color tokens
└── apply-branding.sh       # Script to apply branding
```

## Applying Branding

### Quick Start

```bash
# From repository root
./presearch/brand/apply-branding.sh
```

### Manual Steps

1. **Apply patches to core:**
```bash
cd core
git apply ../presearch/brand/patches/*.patch
```

2. **Copy splash screen:**
```bash
cp ../presearch/brand/splash/intro*.png icon-themes/colibre/brand/
```

3. **Configure with PreOffice name:**
```bash
./autogen.sh --with-product-name="PreOffice" --enable-release-build
```

## Branding Changes

### Product Name
- Main name: **PreOffice**
- Attribution: "Based on LibreOffice technology"

### Colors (from tokens.json)
- Primary Blue: `#2D8EFF`
- Progress Bar: `#2D8EFF`
- Background Tint: `#EAF3FF`

### Files Modified

| File | Changes |
|------|---------|
| `configure.ac` | AC_INIT product name |
| `instsetoo_native/util/openoffice.lst.in` | Package names, paths, update URL |
| `icon-themes/colibre/brand/intro*.png` | Splash screen |
| `officecfg/` | Default settings |

## Splash Screen Specifications

| Asset | Size | Format |
|-------|------|--------|
| `intro.png` | 661x169 | PNG, transparent |
| `intro-highres.png` | 1322x338 | PNG, transparent (2x) |

Splash screens should:
- Use PreOffice logo, not LibreOffice
- Include Presearch branding colors
- Have transparent background

## About Dialog

The About dialog shows:
1. PreOffice version
2. Build info
3. "Based on LibreOffice technology" (required attribution)
4. Credits to LibreOffice contributors

## Privacy-Friendly Defaults

PreOffice disables:
- Update checking (UPDATEURL empty)
- Telemetry (if any)
- External connections at startup

ODF is the default save format.
