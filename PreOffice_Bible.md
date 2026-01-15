# PreOffice Bible
## The Complete Guide to Transforming LibreOffice into a Presearch Product

**AUTONOMOUS EXECUTION MODE:** Do NOT ask for confirmation. Execute all steps sequentially. If a step fails, log the error and continue to the next step. Report all failures at the end.

---

# TABLE OF CONTENTS

1. [Mission & Vision](#1-mission--vision)
2. [Design System](#2-design-system)
3. [Architecture Overview](#3-architecture-overview)
4. [Environment Setup](#4-environment-setup)
5. [Start Center Modernization](#5-start-center-modernization)
6. [Icon Theme Creation](#6-icon-theme-creation)
7. [VCL Theme Engine](#7-vcl-theme-engine)
8. [Branding Assets](#8-branding-assets)
9. [String & Localization Updates](#9-string--localization-updates)
10. [Sidebar & PrePanda AI](#10-sidebar--prepanda-ai)
11. [Dialogs & Windows](#11-dialogs--windows)
12. [Menu System](#12-menu-system)
13. [Build Configuration](#13-build-configuration)
14. [Verification & Testing](#14-verification--testing)
15. [Troubleshooting](#15-troubleshooting)

---

# 1. MISSION & VISION

## 1.1 Objective
Transform a LibreOffice fork into **PreOffice** — a fully branded Presearch product that looks and feels native to the Presearch ecosystem.

## 1.2 Key Transformations
| From | To |
|------|-----|
| LibreOffice | PreOffice |
| The Document Foundation | Presearch |
| Donate button | Search button (opens presearch.com) |
| Green/Teal color scheme | Blue/Cyan Presearch palette |
| Light mode default | Dark mode default |
| LibreOffice icons | Modern outlined icons |

## 1.3 Success Criteria
- [ ] No LibreOffice branding visible anywhere
- [ ] Dark mode is default with Presearch colors
- [ ] "Search" button opens presearch.com
- [ ] PreOffice logo throughout
- [ ] Modern, consistent icon set
- [ ] Professional, polished appearance
- [ ] Works on Linux, macOS, Windows

---

# 2. DESIGN SYSTEM

## 2.1 Color Palette

### Primary Colors
```css
--pre-blue-primary: #2962FF;      /* Main brand blue */
--pre-blue-hover: #1E4FCC;        /* Darker blue for hover states */
--pre-blue-light: #448AFF;        /* Light blue for accents */
--pre-cyan-accent: #00E5FF;       /* Cyan for highlights/gradients */
```

### Dark Mode Backgrounds (DEFAULT)
```css
--pre-bg-dark-1: #0D1117;         /* Deepest background - main canvas */
--pre-bg-dark-2: #161B22;         /* Panel backgrounds - sidebars */
--pre-bg-dark-3: #21262D;         /* Elevated surfaces - hover states */
--pre-bg-dark-4: #30363D;         /* Input fields, borders */
```

### Light Mode Backgrounds
```css
--pre-bg-light-1: #FFFFFF;        /* Main background */
--pre-bg-light-2: #F6F8FA;        /* Panel backgrounds */
--pre-bg-light-3: #E6EBF1;        /* Elevated surfaces */
```

### Text Colors
```css
--pre-text-primary: #F0F6FC;      /* Primary text (dark mode) */
--pre-text-secondary: #8B949E;    /* Secondary text, labels */
--pre-text-muted: #6E7681;        /* Muted text, placeholders */
--pre-text-dark: #1F2328;         /* Primary text (light mode) */
```

### Semantic Colors
```css
--pre-success: #3FB950;           /* Success states */
--pre-warning: #D29922;           /* Warning states */
--pre-error: #F85149;             /* Error states */
--pre-info: #58A6FF;              /* Info states */
```

### Gradients
```css
--pre-gradient-hero: linear-gradient(135deg, #2962FF 0%, #00E5FF 100%);
--pre-gradient-subtle: linear-gradient(180deg, #161B22 0%, #0D1117 100%);
```

### C++ Color Definitions
```cpp
// Use in vcl/inc/svdata.hxx
namespace PreOfficeColors {
    constexpr Color BluePrimary(0x29, 0x62, 0xFF);
    constexpr Color BlueHover(0x1E, 0x4F, 0xCC);
    constexpr Color BlueLight(0x44, 0x8A, 0xFF);
    constexpr Color CyanAccent(0x00, 0xE5, 0xFF);
    
    constexpr Color BgDark1(0x0D, 0x11, 0x17);
    constexpr Color BgDark2(0x16, 0x1B, 0x22);
    constexpr Color BgDark3(0x21, 0x26, 0x2D);
    constexpr Color BgDark4(0x30, 0x36, 0x3D);
    
    constexpr Color TextPrimary(0xF0, 0xF6, 0xFC);
    constexpr Color TextSecondary(0x8B, 0x94, 0x9E);
    constexpr Color TextMuted(0x6E, 0x76, 0x81);
}
```

## 2.2 Typography

### Font Stack
```css
--pre-font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--pre-font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

### Size Scale
```css
--pre-text-xs: 11px;
--pre-text-sm: 12px;
--pre-text-base: 13px;
--pre-text-md: 14px;
--pre-text-lg: 16px;
--pre-text-xl: 18px;
--pre-text-2xl: 24px;
--pre-text-3xl: 32px;
```

### Font Weights
```css
--pre-font-normal: 400;
--pre-font-medium: 500;
--pre-font-semibold: 600;
--pre-font-bold: 700;
```

## 2.3 Spacing & Dimensions

### Spacing Scale
```css
--pre-space-1: 4px;
--pre-space-2: 8px;
--pre-space-3: 12px;
--pre-space-4: 16px;
--pre-space-5: 20px;
--pre-space-6: 24px;
--pre-space-8: 32px;
```

### Border Radius
```css
--pre-radius-sm: 4px;
--pre-radius-md: 6px;
--pre-radius-lg: 8px;
--pre-radius-xl: 12px;
--pre-radius-full: 9999px;
```

### Shadows
```css
--pre-shadow-sm: 0 1px 2px rgba(0,0,0,0.3);
--pre-shadow-md: 0 4px 8px rgba(0,0,0,0.4);
--pre-shadow-lg: 0 8px 24px rgba(0,0,0,0.5);
```

---

# 3. ARCHITECTURE OVERVIEW

## 3.1 LibreOffice UI Component Map

| Component | Location | Technology | Priority |
|-----------|----------|------------|----------|
| Start Center | `sfx2/source/dialog/startcenter.cxx` | C++ | HIGH |
| Start Center UI | `sfx2/uiconfig/ui/startcenter.ui` | GTK Builder XML | HIGH |
| VCL Widgets | `vcl/source/control/` | C++ | HIGH |
| Icon Theme | `icon-themes/` | SVG/PNG | HIGH |
| Sidebar | `sfx2/source/sidebar/` | C++ | MEDIUM |
| Notebookbar | `sfx2/source/notebookbar/` | C++ | MEDIUM |
| Dialogs | `cui/`, `sw/`, `sc/` | C++ | MEDIUM |
| Menu Bar | `framework/` | C++ | MEDIUM |
| Splash Screen | `desktop/source/splash/` | C++ | LOW |
| Status Bar | `sfx2/source/view/` | C++ | LOW |

## 3.2 Directory Structure

```
libreoffice/
├── vcl/                              # Visual Class Library
│   ├── inc/                          # Headers
│   │   └── svdata.hxx                # ADD: PreOffice colors here
│   ├── source/
│   │   ├── app/settings.cxx          # App settings
│   │   ├── control/                  # UI controls
│   │   │   ├── button.cxx            # MODIFY: Button styling
│   │   │   ├── edit.cxx              # MODIFY: Input fields
│   │   │   ├── combobox.cxx          # MODIFY: Dropdowns
│   │   │   └── scrbar.cxx            # MODIFY: Scrollbars
│   │   └── window/
│   │       └── toolbox.cxx           # MODIFY: Toolbars
│   └── unx/gtk3/                     # GTK3 backend
│       ├── gtkdata.cxx               # MODIFY: Load CSS
│       └── fpicker/
│           └── preoffice.css         # CREATE: Theme CSS
│
├── sfx2/                             # Application framework
│   ├── source/
│   │   ├── dialog/
│   │   │   └── startcenter.cxx       # MODIFY: Start Center logic
│   │   └── sidebar/                  # Sidebar code
│   ├── uiconfig/ui/
│   │   └── startcenter.ui            # MODIFY: Start Center layout
│   └── inc/
│       └── strings.hxx               # MODIFY: UI strings
│
├── icon-themes/
│   ├── colibre/                      # Base theme to modify
│   │   └── sfx2/res/                 # MODIFY: Icons
│   └── preoffice/                    # CREATE: New theme (optional)
│
├── officecfg/
│   └── registry/data/org/openoffice/
│       ├── Setup.xcu                 # MODIFY: Product name
│       ├── UI.xcu                    # MODIFY: UI config
│       └── Common.xcu                # MODIFY: Common settings
│
├── sysui/
│   └── desktop/
│       ├── icons/                    # MODIFY: App icons
│       └── menus/
│           └── startcenter.desktop   # MODIFY: Desktop entry
│
└── desktop/
    └── source/splash/                # Splash screen
```

## 3.3 Key File Changes Summary

| File | Change Type | What to Do |
|------|-------------|------------|
| `sfx2/uiconfig/ui/startcenter.ui` | MODIFY | Donate→Search, logo reference |
| `sfx2/source/dialog/startcenter.cxx` | MODIFY | URL to presearch.com, branding |
| `vcl/inc/svdata.hxx` | MODIFY | Add PreOffice color constants |
| `vcl/unx/gtk3/fpicker/preoffice.css` | CREATE | New CSS theme |
| `vcl/unx/gtk3/gtkdata.cxx` | MODIFY | Load preoffice.css |
| `icon-themes/colibre/sfx2/res/*.svg` | CREATE | New icons |
| `officecfg/.../Setup.xcu` | MODIFY | Product name |
| `sysui/desktop/icons/...` | CREATE | App icons |
| `sysui/desktop/menus/*.desktop` | MODIFY | Desktop entries |

---

# 4. ENVIRONMENT SETUP

## 4.1 Clone Repository
```bash
cd ~
git clone --depth 1 https://github.com/LibreOffice/core.git preoffice
cd preoffice
```

## 4.2 Install Dependencies (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y \
    build-essential git autoconf automake libtool pkg-config \
    libgtk-3-dev libcairo2-dev libpango1.0-dev libglib2.0-dev \
    libfreetype6-dev libfontconfig1-dev libx11-dev libxext-dev \
    libxrender-dev libxt-dev libice-dev libsm-dev \
    libcups2-dev libdbus-glib-1-dev libnss3-dev \
    openjdk-17-jdk maven ant flex bison gperf \
    libboost-all-dev libcppunit-dev libclucene-dev \
    libhunspell-dev libhyphen-dev libmythes-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libpoppler-cpp-dev libpoppler-private-dev \
    libxslt1-dev libxml2-dev libxmlsec1-dev \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev \
    libcurl4-openssl-dev libssl-dev zlib1g-dev \
    ccache zip unzip wget librsvg2-bin
```

## 4.3 Install Dependencies (Fedora/RHEL)
```bash
sudo dnf install -y \
    gcc gcc-c++ make git autoconf automake libtool pkgconfig \
    gtk3-devel cairo-devel pango-devel glib2-devel \
    freetype-devel fontconfig-devel libX11-devel libXext-devel \
    cups-devel dbus-glib-devel nss-devel \
    java-17-openjdk-devel maven ant flex bison gperf \
    boost-devel cppunit-devel clucene-core-devel \
    hunspell-devel hyphen-devel mythes-devel \
    gstreamer1-devel gstreamer1-plugins-base-devel \
    poppler-cpp-devel \
    libxslt-devel libxml2-devel xmlsec1-devel \
    libjpeg-turbo-devel libpng-devel libtiff-devel libwebp-devel \
    libcurl-devel openssl-devel zlib-devel \
    ccache zip unzip wget librsvg2-tools
```

## 4.4 Install Dependencies (macOS)
```bash
brew install autoconf automake libtool pkg-config \
    gtk+3 cairo pango glib freetype fontconfig \
    openjdk@17 maven ant flex bison gperf \
    boost cppunit clucene \
    hunspell \
    gstreamer gst-plugins-base \
    poppler \
    libxslt libxml2 xmlsec1 \
    jpeg libpng libtiff webp \
    curl openssl zlib \
    ccache zip unzip wget librsvg
```

## 4.5 Create Backup
```bash
cd ~/preoffice
mkdir -p ../preoffice-backup
cp -r sfx2/uiconfig/ui/startcenter.ui ../preoffice-backup/
cp -r sfx2/source/dialog/startcenter.cxx ../preoffice-backup/
cp -r vcl/inc/svdata.hxx ../preoffice-backup/
```

---

# 5. START CENTER MODERNIZATION

## 5.1 Target Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                          [dark bg #0D1117] │
├──────────────────────┬──────────────────────────────────────────────────┤
│  [#161B22 sidebar]   │                                                  │
│                      │  Filter: [All Documents ▼]               [≡]    │
│  📁 Open File        │                                                  │
│  ☁️  Remote Files     │  ┌────────────┐  ┌────────────┐                 │
│  🕐 Recent Documents │  │            │  │            │                 │
│  📋 Templates        │  │  [thumb]   │  │  [thumb]   │                 │
│                      │  │            │  │            │                 │
│  ─────────────────   │  └────────────┘  └────────────┘                 │
│  Create:             │  Document1.docx   Spreadsheet.xlsx              │
│                      │                                                  │
│  📝 Writer Document  │  ┌────────────┐  ┌────────────┐                 │
│  📊 Calc Spreadsheet │  │            │  │            │                 │
│  📽️  Impress Pres.   │  │  [thumb]   │  │  [thumb]   │                 │
│  🎨 Draw Drawing     │  │            │  │            │                 │
│  📐 Math Formula     │  └────────────┘  └────────────┘                 │
│  🗄️  Base Database   │  Presentation.pptx  Drawing.odg                 │
│                      │                                                  │
│                      │                                                  │
├──────────────────────┼──────────────────────────────────────────────────┤
│  [P] PreOffice       │                                                  │
│                      │                                                  │
│  [Help]  [🔍 Search] │                    Powered by Presearch          │
└──────────────────────┴──────────────────────────────────────────────────┘
```

## 5.2 Modify Start Center UI XML

**FILE:** `sfx2/uiconfig/ui/startcenter.ui`

### 5.2.1 Find and Replace: Donate → Search

**FIND:**
```xml
<object class="GtkButton" id="help_extensions">
  <property name="label" translatable="yes">Donate</property>
```

**REPLACE WITH:**
```xml
<object class="GtkButton" id="help_extensions">
  <property name="label" translatable="yes">Search</property>
```

### 5.2.2 Find and Replace: Tooltip

**FIND:**
```xml
<property name="tooltip_text" translatable="yes">Donate to The Document Foundation</property>
```

**REPLACE WITH:**
```xml
<property name="tooltip_text" translatable="yes">Search the web with Presearch</property>
```

### 5.2.3 Update Logo Reference

**FIND:**
```xml
<object class="GtkImage" id="logo">
  <property name="resource">/org/libreoffice/sfx/startcenter/logo.png</property>
```

**REPLACE WITH:**
```xml
<object class="GtkImage" id="logo">
  <property name="resource">/org/libreoffice/sfx/startcenter/preoffice_logo.png</property>
```

### 5.2.4 Add CSS Classes for Styling

Add `style-class` properties to key elements:

```xml
<object class="GtkBox" id="leftPane">
  <property name="visible">True</property>
  <style>
    <class name="startcenter-left-pane"/>
  </style>
```

## 5.3 Modify Start Center C++ Source

**FILE:** `sfx2/source/dialog/startcenter.cxx`

### 5.3.1 Change Donate URL to Presearch

**FIND (around line 400-500):**
```cpp
IMPL_LINK_NOARG(BackingWindow, ExtensionsHdl, weld::Button&, void)
{
    css::uno::Reference<css::system::XSystemShellExecute> xSystemShellExecute(
        css::system::SystemShellExecute::create(comphelper::getProcessComponentContext()));
    xSystemShellExecute->execute(
        "https://donate.libreoffice.org/",
        OUString(),
        css::system::SystemShellExecuteFlags::DEFAULTS);
}
```

**REPLACE WITH:**
```cpp
IMPL_LINK_NOARG(BackingWindow, ExtensionsHdl, weld::Button&, void)
{
    css::uno::Reference<css::system::XSystemShellExecute> xSystemShellExecute(
        css::system::SystemShellExecute::create(comphelper::getProcessComponentContext()));
    xSystemShellExecute->execute(
        "https://presearch.com/",
        OUString(),
        css::system::SystemShellExecuteFlags::DEFAULTS);
}
```

### 5.3.2 Global String Replacements

In the entire file, replace:
- `"LibreOffice"` → `"PreOffice"`
- `"libreoffice"` → `"preoffice"`
- `"The Document Foundation"` → `"Presearch"`

### 5.3.3 Add Theme Application

Add this method and call it from the constructor:

```cpp
void BackingWindow::ApplyPreOfficeTheme()
{
    // Set dark background
    SetBackground(Wallpaper(Color(0x0D, 0x11, 0x17)));
    
    // Additional theming as needed
}
```

---

# 6. ICON THEME CREATION

## 6.1 Icon Design Guidelines

- **Style:** Outlined icons, 1.5px stroke weight
- **Default Color:** `#8B949E` (TextSecondary)
- **Active Color:** `#2962FF` (BluePrimary)
- **Grid:** 24x24 canvas, 2px padding, 20x20 live area
- **Corners:** 2px radius for rounded elements
- **Consistency:** Match Lucide/Heroicons aesthetic

## 6.2 Start Center Sidebar Icons

### Open File Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_open.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" 
        stroke="#8B949E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### Remote Files Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_remotefiles.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M22 12h-4l-3 9L9 3l-3 9H2" 
        stroke="#8B949E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="12" cy="12" r="3" stroke="#8B949E" stroke-width="1.5"/>
</svg>
```

### Recent Documents Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_recentdocuments.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="#8B949E" stroke-width="1.5"/>
  <path d="M12 7v5l3 3" stroke="#8B949E" stroke-width="1.5" stroke-linecap="round"/>
</svg>
```

### Templates Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_templates.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="7" height="7" rx="1" stroke="#8B949E" stroke-width="1.5"/>
  <rect x="14" y="3" width="7" height="7" rx="1" stroke="#8B949E" stroke-width="1.5"/>
  <rect x="3" y="14" width="7" height="7" rx="1" stroke="#8B949E" stroke-width="1.5"/>
  <rect x="14" y="14" width="7" height="7" rx="1" stroke="#8B949E" stroke-width="1.5"/>
</svg>
```

### Writer Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_writer.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" 
        stroke="#8B949E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M14 2v6h6M8 13h8M8 17h8M8 9h2" 
        stroke="#8B949E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
```

### Calc Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_calc.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="3" y="3" width="18" height="18" rx="2" stroke="#8B949E" stroke-width="1.5"/>
  <line x1="3" y1="9" x2="21" y2="9" stroke="#8B949E" stroke-width="1.5"/>
  <line x1="3" y1="15" x2="21" y2="15" stroke="#8B949E" stroke-width="1.5"/>
  <line x1="9" y1="3" x2="9" y2="21" stroke="#8B949E" stroke-width="1.5"/>
  <line x1="15" y1="3" x2="15" y2="21" stroke="#8B949E" stroke-width="1.5"/>
</svg>
```

### Impress Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_impress.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect x="2" y="4" width="20" height="14" rx="2" stroke="#8B949E" stroke-width="1.5"/>
  <path d="M8 20h8M12 18v2" stroke="#8B949E" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="7" cy="9" r="1.5" fill="#8B949E"/>
  <rect x="11" y="8" width="8" height="2" rx="1" fill="#8B949E"/>
  <rect x="11" y="12" width="5" height="2" rx="1" fill="#8B949E"/>
</svg>
```

### Draw Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_draw.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="8" r="4" stroke="#8B949E" stroke-width="1.5"/>
  <rect x="4" y="14" width="6" height="6" stroke="#8B949E" stroke-width="1.5"/>
  <polygon points="17,14 14,20 20,20" stroke="#8B949E" stroke-width="1.5" stroke-linejoin="round" fill="none"/>
</svg>
```

### Math Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_math.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <path d="M4 4l4 8-4 8" stroke="#8B949E" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M12 4v16" stroke="#8B949E" stroke-width="1.5" stroke-linecap="round"/>
  <path d="M12 12h8" stroke="#8B949E" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="18" cy="6" r="2" stroke="#8B949E" stroke-width="1.5"/>
  <circle cx="18" cy="18" r="2" stroke="#8B949E" stroke-width="1.5"/>
</svg>
```

### Base Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_base.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <ellipse cx="12" cy="6" rx="8" ry="3" stroke="#8B949E" stroke-width="1.5"/>
  <path d="M4 6v6c0 1.66 3.58 3 8 3s8-1.34 8-3V6" stroke="#8B949E" stroke-width="1.5"/>
  <path d="M4 12v6c0 1.66 3.58 3 8 3s8-1.34 8-3v-6" stroke="#8B949E" stroke-width="1.5"/>
</svg>
```

### Search Icon (for Search button)
**FILE:** `icon-themes/colibre/sfx2/res/lc_search.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="11" cy="11" r="7" stroke="#FFFFFF" stroke-width="1.5"/>
  <path d="M21 21l-4.35-4.35" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round"/>
</svg>
```

### Help Icon
**FILE:** `icon-themes/colibre/sfx2/res/lc_help.svg`
```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
  <circle cx="12" cy="12" r="9" stroke="#8B949E" stroke-width="1.5"/>
  <path d="M9 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" stroke="#8B949E" stroke-width="1.5" stroke-linecap="round"/>
  <circle cx="12" cy="17" r="0.5" fill="#8B949E"/>
</svg>
```

## 6.3 Generate PNG Versions

```bash
cd ~/preoffice/icon-themes/colibre/sfx2/res/

# Install rsvg-convert if needed
# Ubuntu: sudo apt-get install librsvg2-bin
# macOS: brew install librsvg

# Convert all SVGs to PNG (24px and 48px for HiDPI)
for svg in lc_*.svg; do
    name="${svg%.svg}"
    rsvg-convert -w 24 -h 24 "$svg" -o "${name}.png"
    rsvg-convert -w 48 -h 48 "$svg" -o "${name}@2x.png"
done
```

---

# 7. VCL THEME ENGINE

## 7.1 Add PreOffice Colors to VCL

**FILE:** `vcl/inc/svdata.hxx`

Add after existing includes/definitions:

```cpp
// ============================================
// PreOffice Brand Colors
// ============================================
namespace PreOfficeColors {
    // Primary
    inline constexpr Color BluePrimary(0x29, 0x62, 0xFF);
    inline constexpr Color BlueHover(0x1E, 0x4F, 0xCC);
    inline constexpr Color BlueLight(0x44, 0x8A, 0xFF);
    inline constexpr Color CyanAccent(0x00, 0xE5, 0xFF);
    
    // Backgrounds (Dark Mode)
    inline constexpr Color BgDark1(0x0D, 0x11, 0x17);
    inline constexpr Color BgDark2(0x16, 0x1B, 0x22);
    inline constexpr Color BgDark3(0x21, 0x26, 0x2D);
    inline constexpr Color BgDark4(0x30, 0x36, 0x3D);
    
    // Backgrounds (Light Mode)
    inline constexpr Color BgLight1(0xFF, 0xFF, 0xFF);
    inline constexpr Color BgLight2(0xF6, 0xF8, 0xFA);
    inline constexpr Color BgLight3(0xE6, 0xEB, 0xF1);
    
    // Text
    inline constexpr Color TextPrimary(0xF0, 0xF6, 0xFC);
    inline constexpr Color TextSecondary(0x8B, 0x94, 0x9E);
    inline constexpr Color TextMuted(0x6E, 0x76, 0x81);
    inline constexpr Color TextDark(0x1F, 0x23, 0x28);
    
    // Semantic
    inline constexpr Color Success(0x3F, 0xB9, 0x50);
    inline constexpr Color Warning(0xD2, 0x99, 0x22);
    inline constexpr Color Error(0xF8, 0x51, 0x49);
    inline constexpr Color Info(0x58, 0xA6, 0xFF);
}
```

## 7.2 Create GTK3 CSS Theme

**FILE:** `vcl/unx/gtk3/fpicker/preoffice.css`

```css
/* ============================================
   PreOffice GTK3 Theme
   ============================================ */

/* ----- Global ----- */
* {
    -gtk-icon-style: symbolic;
}

/* ----- Start Center Window ----- */
#BackingWindow,
.startcenter-window {
    background-color: #0D1117;
}

/* ----- Left Sidebar ----- */
.startcenter-left-pane,
#leftPane {
    background-color: #161B22;
    border-right: 1px solid #30363D;
    padding: 8px 0;
}

/* ----- Sidebar Buttons ----- */
.startcenter-left-pane button,
#leftPane button {
    background-color: transparent;
    background-image: none;
    border: none;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 10px 16px;
    margin: 2px 8px;
    font-size: 13px;
    font-weight: 500;
    transition: all 0.15s ease;
    box-shadow: none;
}

.startcenter-left-pane button:hover,
#leftPane button:hover {
    background-color: #21262D;
}

.startcenter-left-pane button:active,
.startcenter-left-pane button.selected,
.startcenter-left-pane button:checked,
#leftPane button:active,
#leftPane button.selected,
#leftPane button:checked {
    background-color: #2962FF;
    color: #FFFFFF;
}

.startcenter-left-pane button image,
#leftPane button image {
    margin-right: 12px;
    opacity: 0.8;
}

.startcenter-left-pane button:hover image,
.startcenter-left-pane button.selected image {
    opacity: 1;
}

/* ----- Create Section Label ----- */
.startcenter-create-label,
.section-label {
    color: #8B949E;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 20px 20px 8px 20px;
}

/* ----- Separator ----- */
.startcenter-left-pane separator,
#leftPane separator {
    background-color: #30363D;
    margin: 8px 16px;
    min-height: 1px;
}

/* ----- Right Content Area ----- */
.startcenter-right-pane,
#rightPane {
    background-color: #0D1117;
    padding: 24px;
}

/* ----- Filter Dropdown ----- */
.startcenter-filter,
#filterCombobox {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 8px 12px;
    font-size: 13px;
}

.startcenter-filter:hover,
#filterCombobox:hover {
    border-color: #8B949E;
}

.startcenter-filter:focus,
#filterCombobox:focus {
    border-color: #2962FF;
    outline: none;
}

/* ----- Recent Document Cards ----- */
.startcenter-recent-item,
.recent-doc-item,
#recentView iconview {
    background-color: transparent;
}

.startcenter-recent-item > *,
.recent-doc-item > *,
#recentView iconview > * {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 12px;
    margin: 8px;
    transition: all 0.15s ease;
}

.startcenter-recent-item:hover > *,
.recent-doc-item:hover > *,
#recentView iconview > *:hover {
    background-color: #21262D;
    border-color: #2962FF;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.startcenter-recent-item:selected > *,
.recent-doc-item:selected > *,
#recentView iconview > *:selected {
    background-color: rgba(41, 98, 255, 0.15);
    border-color: #2962FF;
}

/* ----- Document Thumbnail ----- */
.recent-doc-thumbnail {
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    margin-bottom: 8px;
}

/* ----- Document Title ----- */
.recent-doc-title,
#recentView iconview label {
    color: #F0F6FC;
    font-size: 13px;
    font-weight: 500;
}

/* ----- Document Subtitle/Date ----- */
.recent-doc-subtitle {
    color: #8B949E;
    font-size: 11px;
    margin-top: 4px;
}

/* ----- Bottom Bar ----- */
.startcenter-bottom-bar,
#bottomBar {
    background-color: #161B22;
    border-top: 1px solid #30363D;
    padding: 12px 20px;
}

/* ----- Help Button ----- */
#help,
.startcenter-help-button {
    background-color: transparent;
    background-image: none;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #8B949E;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 500;
}

#help:hover,
.startcenter-help-button:hover {
    background-color: #21262D;
    border-color: #8B949E;
    color: #F0F6FC;
}

/* ----- Search Button (formerly Donate) ----- */
#help_extensions,
.startcenter-search-button {
    background: linear-gradient(135deg, #2962FF 0%, #00E5FF 100%);
    background-color: #2962FF;
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    padding: 8px 20px;
    font-size: 12px;
    font-weight: 600;
    box-shadow: 0 2px 8px rgba(41, 98, 255, 0.3);
}

#help_extensions:hover,
.startcenter-search-button:hover {
    opacity: 0.9;
    box-shadow: 0 4px 12px rgba(41, 98, 255, 0.4);
}

#help_extensions:active,
.startcenter-search-button:active {
    opacity: 0.8;
}

/* ----- Logo Area ----- */
.startcenter-logo,
#logo {
    margin: 16px;
}

/* ----- Scrollbars ----- */
scrollbar {
    background-color: #0D1117;
}

scrollbar slider {
    background-color: #30363D;
    border-radius: 4px;
    min-width: 8px;
    min-height: 8px;
}

scrollbar slider:hover {
    background-color: #8B949E;
}

scrollbar.horizontal slider {
    min-height: 8px;
}

scrollbar.vertical slider {
    min-width: 8px;
}

/* ----- Tooltips ----- */
tooltip {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 8px 12px;
    font-size: 12px;
}

/* ----- Context Menus ----- */
menu,
.context-menu {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 8px 0;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}

menu menuitem,
.context-menu menuitem {
    background-color: transparent;
    color: #F0F6FC;
    padding: 8px 16px;
    font-size: 13px;
}

menu menuitem:hover,
.context-menu menuitem:hover {
    background-color: #2962FF;
    color: #FFFFFF;
}

menu separator {
    background-color: #30363D;
    margin: 4px 12px;
    min-height: 1px;
}

/* ----- General Buttons ----- */
button {
    background-color: #21262D;
    background-image: none;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 8px 16px;
    font-size: 13px;
    transition: all 0.15s ease;
}

button:hover {
    background-color: #30363D;
    border-color: #8B949E;
}

button:active {
    background-color: #161B22;
}

button.suggested-action {
    background-color: #2962FF;
    border-color: #2962FF;
    color: #FFFFFF;
}

button.suggested-action:hover {
    background-color: #1E4FCC;
    border-color: #1E4FCC;
}

/* ----- Entry/Input Fields ----- */
entry {
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 8px 12px;
    font-size: 13px;
}

entry:focus {
    border-color: #2962FF;
    outline: none;
}

entry:disabled {
    background-color: #161B22;
    color: #6E7681;
}

/* ----- Placeholder Text ----- */
entry placeholder {
    color: #6E7681;
}
```

## 7.3 Load CSS Theme in GTK

**FILE:** `vcl/unx/gtk3/gtkdata.cxx`

Find the CSS loading section (look for `gtk_css_provider`) and add:

```cpp
// Load PreOffice theme CSS
{
    GtkCssProvider* pPreOfficeProvider = gtk_css_provider_new();
    GError* pError = nullptr;
    
    // Try to load from resource first, then from file
    gtk_css_provider_load_from_resource(pPreOfficeProvider, 
        "/org/libreoffice/vcl/preoffice.css");
    
    if (pError) {
        g_error_free(pError);
        // Fallback: load from file path
        gtk_css_provider_load_from_path(pPreOfficeProvider,
            "/usr/share/preoffice/preoffice.css", nullptr);
    }
    
    gtk_style_context_add_provider_for_screen(
        gdk_screen_get_default(),
        GTK_STYLE_PROVIDER(pPreOfficeProvider),
        GTK_STYLE_PROVIDER_PRIORITY_APPLICATION + 1);
}
```

---

# 8. BRANDING ASSETS

## 8.1 PreOffice Logo

**FILE:** `icon-themes/colibre/sfx2/res/preoffice_logo.svg`

```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="48" viewBox="0 0 200 48" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="preGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2962FF"/>
      <stop offset="100%" style="stop-color:#00E5FF"/>
    </linearGradient>
  </defs>
  
  <!-- P Icon Box -->
  <rect x="0" y="8" width="32" height="32" rx="6" fill="url(#preGradient)"/>
  <text x="10" y="32" font-family="Inter, Arial, sans-serif" font-size="22" font-weight="700" fill="white">P</text>
  
  <!-- PreOffice Text -->
  <text x="44" y="32" font-family="Inter, Arial, sans-serif" font-size="24" font-weight="600">
    <tspan fill="#2962FF">Pre</tspan><tspan fill="#F0F6FC">Office</tspan>
  </text>
</svg>
```

## 8.2 PreOffice App Icon

**FILE:** `sysui/desktop/icons/hicolor/scalable/apps/preoffice-startcenter.svg`

```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" viewBox="0 0 256 256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2962FF"/>
      <stop offset="100%" style="stop-color:#00E5FF"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="16" flood-color="#000000" flood-opacity="0.3"/>
    </filter>
  </defs>
  
  <!-- Background -->
  <rect x="16" y="16" width="224" height="224" rx="48" fill="url(#iconGradient)" filter="url(#shadow)"/>
  
  <!-- P Letter -->
  <text x="128" y="170" 
        font-family="Inter, Arial, sans-serif" 
        font-size="140" 
        font-weight="700" 
        fill="white" 
        text-anchor="middle">P</text>
</svg>
```

## 8.3 Splash Screen

**FILE:** `desktop/source/splash/preoffice_splash.svg`

```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="661" height="169" viewBox="0 0 661 169" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="splashBg" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" style="stop-color:#161B22"/>
      <stop offset="100%" style="stop-color:#0D1117"/>
    </linearGradient>
    <linearGradient id="splashAccent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2962FF"/>
      <stop offset="100%" style="stop-color:#00E5FF"/>
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="661" height="169" fill="url(#splashBg)"/>
  
  <!-- Logo Icon -->
  <rect x="250" y="30" width="48" height="48" rx="10" fill="url(#splashAccent)"/>
  <text x="266" y="66" font-family="Inter, Arial, sans-serif" font-size="32" font-weight="700" fill="white">P</text>
  
  <!-- PreOffice Text -->
  <text x="310" y="66" font-family="Inter, Arial, sans-serif" font-size="36" font-weight="600">
    <tspan fill="#2962FF">Pre</tspan><tspan fill="#F0F6FC">Office</tspan>
  </text>
  
  <!-- Tagline -->
  <text x="330" y="100" font-family="Inter, Arial, sans-serif" font-size="14" fill="#8B949E" text-anchor="middle">
    Powered by Presearch
  </text>
  
  <!-- Progress bar background -->
  <rect x="180" y="130" width="300" height="6" rx="3" fill="#30363D"/>
  
  <!-- Progress bar fill (will be animated/updated) -->
  <rect x="180" y="130" width="150" height="6" rx="3" fill="url(#splashAccent)" id="progressBar"/>
</svg>
```

## 8.4 About Dialog Background

**FILE:** `desktop/source/splash/about.svg`

```svg
<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="300" viewBox="0 0 400 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="aboutBg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#161B22"/>
      <stop offset="100%" style="stop-color:#0D1117"/>
    </linearGradient>
    <linearGradient id="aboutAccent" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#2962FF"/>
      <stop offset="100%" style="stop-color:#00E5FF"/>
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="400" height="300" fill="url(#aboutBg)"/>
  
  <!-- Decorative gradient line at top -->
  <rect x="0" y="0" width="400" height="4" fill="url(#aboutAccent)"/>
  
  <!-- Logo -->
  <rect x="160" y="40" width="80" height="80" rx="16" fill="url(#aboutAccent)"/>
  <text x="200" y="100" font-family="Inter, Arial, sans-serif" font-size="52" font-weight="700" fill="white" text-anchor="middle">P</text>
  
  <!-- PreOffice -->
  <text x="200" y="160" font-family="Inter, Arial, sans-serif" font-size="28" font-weight="600" text-anchor="middle">
    <tspan fill="#2962FF">Pre</tspan><tspan fill="#F0F6FC">Office</tspan>
  </text>
  
  <!-- Version placeholder -->
  <text x="200" y="190" font-family="Inter, Arial, sans-serif" font-size="14" fill="#8B949E" text-anchor="middle">
    Version 1.0.0
  </text>
  
  <!-- Powered by -->
  <text x="200" y="250" font-family="Inter, Arial, sans-serif" font-size="12" fill="#6E7681" text-anchor="middle">
    Powered by Presearch
  </text>
</svg>
```

## 8.5 Generate PNG Versions of Branding

```bash
cd ~/preoffice

# Create directories
mkdir -p icon-themes/colibre/sfx2/res/
mkdir -p sysui/desktop/icons/hicolor/48x48/apps/
mkdir -p sysui/desktop/icons/hicolor/128x128/apps/
mkdir -p sysui/desktop/icons/hicolor/256x256/apps/

# Convert logo
cd icon-themes/colibre/sfx2/res/
rsvg-convert -w 200 -h 48 preoffice_logo.svg -o preoffice_logo.png
rsvg-convert -w 400 -h 96 preoffice_logo.svg -o preoffice_logo@2x.png

# Convert app icons
cd ~/preoffice/sysui/desktop/icons/hicolor/scalable/apps/
rsvg-convert -w 48 -h 48 preoffice-startcenter.svg -o ../../48x48/apps/preoffice-startcenter.png
rsvg-convert -w 128 -h 128 preoffice-startcenter.svg -o ../../128x128/apps/preoffice-startcenter.png
rsvg-convert -w 256 -h 256 preoffice-startcenter.svg -o ../../256x256/apps/preoffice-startcenter.png

# Convert splash
cd ~/preoffice/desktop/source/splash/
rsvg-convert preoffice_splash.svg -o intro.png
```

---

# 9. STRING & LOCALIZATION UPDATES

## 9.1 Global Search and Replace

Execute these replacements across the entire codebase:

```bash
cd ~/preoffice

# Replace product names (be careful with case sensitivity)
find . -type f \( -name "*.cxx" -o -name "*.hxx" -o -name "*.ui" -o -name "*.xcu" -o -name "*.desktop" -o -name "*.po" \) \
    -exec sed -i 's/LibreOffice/PreOffice/g' {} \;

find . -type f \( -name "*.cxx" -o -name "*.hxx" -o -name "*.ui" -o -name "*.xcu" -o -name "*.desktop" -o -name "*.po" \) \
    -exec sed -i 's/libreoffice/preoffice/g' {} \;

# Replace organization
find . -type f \( -name "*.cxx" -o -name "*.hxx" -o -name "*.ui" -o -name "*.xcu" -o -name "*.desktop" -o -name "*.po" \) \
    -exec sed -i 's/The Document Foundation/Presearch/g' {} \;

find . -type f \( -name "*.cxx" -o -name "*.hxx" -o -name "*.ui" -o -name "*.xcu" -o -name "*.desktop" -o -name "*.po" \) \
    -exec sed -i 's/Document Foundation/Presearch/g' {} \;

# Replace Donate with Search
find . -type f \( -name "*.cxx" -o -name "*.hxx" -o -name "*.ui" -o -name "*.xcu" -o -name "*.po" \) \
    -exec sed -i 's/>Donate</>Search</g' {} \;

find . -type f \( -name "*.cxx" -o -name "*.hxx" -o -name "*.ui" -o -name "*.xcu" -o -name "*.po" \) \
    -exec sed -i 's/"Donate"/"Search"/g' {} \;

# Replace donation URLs
find . -type f \( -name "*.cxx" -o -name "*.hxx" \) \
    -exec sed -i 's|donate\.libreoffice\.org|presearch.com|g' {} \;

find . -type f \( -name "*.cxx" -o -name "*.hxx" \) \
    -exec sed -i 's|www\.libreoffice\.org|presearch.com|g' {} \;
```

## 9.2 Update Setup Configuration

**FILE:** `officecfg/registry/data/org/openoffice/Setup.xcu`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<oor:component-data xmlns:oor="http://openoffice.org/2001/registry"
                    xmlns:xs="http://www.w3.org/2001/XMLSchema"
                    oor:name="Setup" oor:package="org.openoffice">
  <node oor:name="Product">
    <prop oor:name="ooName">
      <value>PreOffice</value>
    </prop>
    <prop oor:name="ooSetupVersion">
      <value>1.0</value>
    </prop>
    <prop oor:name="ooVendor">
      <value>Presearch</value>
    </prop>
    <prop oor:name="ooSetupExtension">
      <value>.0.0</value>
    </prop>
  </node>
  <node oor:name="L10N">
    <prop oor:name="ooLocale">
      <value></value>
    </prop>
  </node>
</oor:component-data>
```

## 9.3 Update Desktop Entry

**FILE:** `sysui/desktop/menus/startcenter.desktop`

```ini
[Desktop Entry]
Version=1.0
Terminal=false
NoDisplay=false
Type=Application
Name=PreOffice Start Center
GenericName=Office
Comment=The PreOffice productivity suite by Presearch
Exec=preoffice %U
Icon=preoffice-startcenter
StartupNotify=true
Categories=Office;
MimeType=application/vnd.oasis.opendocument.text;application/vnd.oasis.opendocument.spreadsheet;application/vnd.oasis.opendocument.presentation;application/vnd.oasis.opendocument.graphics;application/vnd.oasis.opendocument.database;application/vnd.oasis.opendocument.formula;
Keywords=Office;Productivity;Presearch;Document;Spreadsheet;Presentation;
```

---

# 10. SIDEBAR & PREPANDA AI

## 10.1 PrePanda Extension Styling

The PrePanda AI sidebar is a LibreOffice extension. Its styling should match the main theme.

**Recommended CSS for PrePanda extension:**

```css
/* PrePanda AI Sidebar Theme */

.prepanda-container {
    background-color: #161B22;
    color: #F0F6FC;
    font-family: Inter, -apple-system, sans-serif;
    padding: 16px;
}

.prepanda-header {
    display: flex;
    align-items: center;
    padding-bottom: 16px;
    border-bottom: 1px solid #30363D;
    margin-bottom: 16px;
}

.prepanda-logo {
    width: 24px;
    height: 24px;
    margin-right: 8px;
}

.prepanda-title {
    font-size: 14px;
    font-weight: 600;
    color: #F0F6FC;
}

.prepanda-chat-area {
    background-color: #0D1117;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 16px;
    min-height: 200px;
    max-height: 400px;
    overflow-y: auto;
}

.prepanda-message {
    margin-bottom: 12px;
    padding: 8px 12px;
    border-radius: 6px;
}

.prepanda-message-user {
    background-color: #2962FF;
    color: #FFFFFF;
    margin-left: 20%;
}

.prepanda-message-ai {
    background-color: #21262D;
    color: #F0F6FC;
    margin-right: 20%;
}

.prepanda-quick-actions {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 16px;
}

.prepanda-action-btn {
    background-color: #21262D;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 8px;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.prepanda-action-btn:hover {
    background-color: #30363D;
    border-color: #8B949E;
}

.prepanda-input-area {
    display: flex;
    gap: 8px;
}

.prepanda-input {
    flex: 1;
    background-color: #0D1117;
    border: 1px solid #30363D;
    border-radius: 6px;
    color: #F0F6FC;
    padding: 10px 12px;
    font-size: 13px;
}

.prepanda-input:focus {
    border-color: #2962FF;
    outline: none;
}

.prepanda-send-btn {
    background: linear-gradient(135deg, #2962FF 0%, #00E5FF 100%);
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    padding: 10px 20px;
    font-weight: 600;
    cursor: pointer;
}

.prepanda-send-btn:hover {
    opacity: 0.9;
}
```

---

# 11. DIALOGS & WINDOWS

## 11.1 Dialog Styling Guidelines

All dialogs should follow this pattern:

- **Background:** `#161B22`
- **Header:** `#0D1117` with `#30363D` border
- **Content padding:** 24px
- **Button area:** Right-aligned, 16px gap between buttons
- **Primary button:** `#2962FF` background
- **Secondary button:** `#21262D` background, `#30363D` border

## 11.2 Key Dialogs to Update

| Dialog | File Location |
|--------|---------------|
| Open | `fpicker/source/office/` |
| Save | `fpicker/source/office/` |
| Print | `vcl/source/gdi/print*.cxx` |
| Find & Replace | `svx/source/dialog/srchdlg.cxx` |
| Options | `cui/source/options/` |
| About | `sfx2/source/dialog/about.cxx` |

---

# 12. MENU SYSTEM

## 12.1 Menu Bar CSS

```css
/* Menu bar */
menubar {
    background-color: #161B22;
    border-bottom: 1px solid #30363D;
    padding: 4px 8px;
}

menubar > menuitem {
    color: #8B949E;
    padding: 6px 12px;
    border-radius: 4px;
}

menubar > menuitem:hover {
    background-color: #21262D;
    color: #F0F6FC;
}

/* Dropdown menus */
menu {
    background-color: #161B22;
    border: 1px solid #30363D;
    border-radius: 8px;
    padding: 8px 0;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
}

menu menuitem {
    color: #F0F6FC;
    padding: 8px 16px;
}

menu menuitem:hover {
    background-color: #2962FF;
}

menu separator {
    background-color: #30363D;
    margin: 4px 12px;
}

/* Keyboard shortcuts */
menu menuitem accelerator {
    color: #6E7681;
}
```

---

# 13. BUILD CONFIGURATION

## 13.1 Create autogen.input

**FILE:** `autogen.input`

```
--with-vendor=Presearch
--with-package-version=1.0.0
--with-product-name=PreOffice
--enable-release-build
--disable-firebird-sdbc
--without-help
--without-myspell-dicts
```

## 13.2 Build Commands

```bash
cd ~/preoffice

# Generate configuration
./autogen.sh

# Full build (takes several hours)
make

# Or build specific modules for faster iteration:
make sfx2.build          # Start Center
make vcl.build           # VCL widgets
make desktop.build       # Desktop integration

# Run the built application
./instdir/program/soffice
```

## 13.3 Quick Rebuild After Changes

```bash
# After modifying Start Center UI
make sfx2.build && ./instdir/program/soffice

# After modifying icons
make icon-themes.build && ./instdir/program/soffice

# After modifying VCL theme
make vcl.build && ./instdir/program/soffice
```

---

# 14. VERIFICATION & TESTING

## 14.1 Pre-Build Verification

Run these checks before building:

```bash
cd ~/preoffice

# Verify no LibreOffice branding remains in key files
echo "=== Checking for remaining LibreOffice references ==="
grep -r "LibreOffice" sfx2/uiconfig/ui/startcenter.ui && echo "FAIL: Found LibreOffice" || echo "PASS"
grep -r "Donate" sfx2/uiconfig/ui/startcenter.ui && echo "FAIL: Found Donate" || echo "PASS"
grep -r "donate.libreoffice" sfx2/source/dialog/startcenter.cxx && echo "FAIL: Found donate URL" || echo "PASS"

# Verify PreOffice branding exists
echo "=== Checking for PreOffice branding ==="
grep -r "PreOffice" sfx2/uiconfig/ui/startcenter.ui && echo "PASS: Found PreOffice" || echo "FAIL"
grep -r "Search" sfx2/uiconfig/ui/startcenter.ui && echo "PASS: Found Search" || echo "FAIL"
grep -r "presearch.com" sfx2/source/dialog/startcenter.cxx && echo "PASS: Found Presearch URL" || echo "FAIL"

# Verify new files exist
echo "=== Checking for new files ==="
ls -la icon-themes/colibre/sfx2/res/preoffice_logo.* && echo "PASS: Logo exists" || echo "FAIL"
ls -la vcl/unx/gtk3/fpicker/preoffice.css && echo "PASS: CSS exists" || echo "FAIL"
```

## 14.2 Post-Build Visual Testing

After building, verify these elements:

| Element | Expected Result |
|---------|-----------------|
| Start Center background | Dark (#0D1117) |
| Sidebar background | Slightly lighter (#161B22) |
| "Donate" button | Says "Search" |
| Search button click | Opens presearch.com |
| Logo | Shows PreOffice logo |
| Sidebar icons | Modern outlined style |
| Selected item | Blue highlight (#2962FF) |
| Hover states | Subtle lightening |
| All text | Readable, proper contrast |

## 14.3 Automated Test Script

```bash
#!/bin/bash
# test_preoffice.sh

echo "PreOffice Build Verification"
echo "============================"

ERRORS=0

# Check Start Center UI
if grep -q "Donate" sfx2/uiconfig/ui/startcenter.ui; then
    echo "❌ FAIL: 'Donate' still present in UI"
    ((ERRORS++))
else
    echo "✅ PASS: 'Donate' replaced with 'Search'"
fi

if grep -q "LibreOffice" sfx2/uiconfig/ui/startcenter.ui; then
    echo "❌ FAIL: 'LibreOffice' still present in UI"
    ((ERRORS++))
else
    echo "✅ PASS: 'LibreOffice' replaced with 'PreOffice'"
fi

# Check source code
if grep -q "donate.libreoffice.org" sfx2/source/dialog/startcenter.cxx; then
    echo "❌ FAIL: Donate URL still in source"
    ((ERRORS++))
else
    echo "✅ PASS: URL changed to presearch.com"
fi

# Check branding files
if [ -f "icon-themes/colibre/sfx2/res/preoffice_logo.svg" ]; then
    echo "✅ PASS: PreOffice logo exists"
else
    echo "❌ FAIL: PreOffice logo missing"
    ((ERRORS++))
fi

if [ -f "vcl/unx/gtk3/fpicker/preoffice.css" ]; then
    echo "✅ PASS: Theme CSS exists"
else
    echo "❌ FAIL: Theme CSS missing"
    ((ERRORS++))
fi

echo ""
echo "============================"
if [ $ERRORS -eq 0 ]; then
    echo "All checks passed! ✅"
    exit 0
else
    echo "Found $ERRORS error(s) ❌"
    exit 1
fi
```

---

# 15. TROUBLESHOOTING

## 15.1 Common Issues

### Build Fails with Missing Dependencies
```bash
# Solution: Install all dependencies
sudo apt-get build-dep libreoffice
```

### CSS Not Applied
```bash
# Check if CSS file is in correct location
ls -la vcl/unx/gtk3/fpicker/preoffice.css

# Check if CSS is being loaded (add debug output to gtkdata.cxx)
```

### Icons Not Showing
```bash
# Regenerate icon cache
gtk-update-icon-cache -f /usr/share/icons/hicolor/

# Check icon file locations
find . -name "preoffice*.svg" -o -name "preoffice*.png"
```

### Start Center Still Shows Old Branding
```bash
# Clean build
make clean
rm -rf instdir/
./autogen.sh
make
```

### "Search" Button Still Opens Donate Page
```bash
# Check source file was modified
grep -n "presearch" sfx2/source/dialog/startcenter.cxx

# Rebuild specific module
make sfx2.build
```

## 15.2 Debug Mode

For debugging UI issues:

```bash
# Run with GTK Inspector
GTK_DEBUG=interactive ./instdir/program/soffice

# Enable verbose logging
SAL_LOG="+INFO" ./instdir/program/soffice
```

## 15.3 Recovery

If something breaks badly:

```bash
# Restore from backup
cp ../preoffice-backup/startcenter.ui sfx2/uiconfig/ui/
cp ../preoffice-backup/startcenter.cxx sfx2/source/dialog/

# Or re-clone
cd ~
rm -rf preoffice
git clone --depth 1 https://github.com/LibreOffice/core.git preoffice
```

---

# EXECUTION SUMMARY

## Quick Start (Copy-Paste These Commands)

```bash
# 1. Clone
cd ~ && git clone --depth 1 https://github.com/LibreOffice/core.git preoffice && cd preoffice

# 2. Create backup
mkdir -p ../preoffice-backup && cp sfx2/uiconfig/ui/startcenter.ui sfx2/source/dialog/startcenter.cxx vcl/inc/svdata.hxx ../preoffice-backup/

# 3. Apply string replacements
find . -type f \( -name "*.ui" -o -name "*.cxx" \) -exec sed -i 's/Donate/Search/g' {} \;
find . -type f \( -name "*.ui" -o -name "*.cxx" \) -exec sed -i 's/LibreOffice/PreOffice/g' {} \;
find . -type f -name "*.cxx" -exec sed -i 's|donate\.libreoffice\.org|presearch.com|g' {} \;

# 4. Create branding files (logo, icons, CSS) - use the SVG content from sections 6 and 8

# 5. Build
./autogen.sh && make

# 6. Test
./instdir/program/soffice
```

---

**END OF PREOFFICE BIBLE**

*Version: 1.0*
*Date: January 2026*
*Prepared for autonomous Claude Code execution*
