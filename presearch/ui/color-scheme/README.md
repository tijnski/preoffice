# PreOffice Color Schemes

This directory contains the color scheme configurations for PreOffice.

## Available Themes

### PreOffice Light (Default)
- **Accent**: #2D8EFF (Presearch Blue)
- **Background**: #FFFFFF
- **Text**: #333333
- Best for: Bright environments, standard office work

### PreOffice Dark
- **Accent**: #5BA3FF (Lighter Blue for dark backgrounds)
- **Background**: #1E1E1E
- **Text**: #E0E0E0
- Best for: Low-light environments, reduced eye strain

### PreOffice High Contrast
- **Accent**: #00BFFF (Bright Cyan)
- **Background**: #000000
- **Text**: #FFFFFF
- Best for: Accessibility, visual impairments

## Configuration Files

| File | Description |
|------|-------------|
| `Appearance.xcu` | Light mode colors |
| `AppearanceDark.xcu` | Dark mode colors |
| `PersonalizationDark.xcu` | Dark mode UI personalization |
| `ThemeRegistry.xcu` | Theme switcher registry |

## Color Reference

### Presearch Brand Colors
| Name | Light Mode | Dark Mode | Decimal |
|------|------------|-----------|---------|
| Primary Blue | #2D8EFF | #5BA3FF | 2985727 / 6005759 |
| Dark Blue | #1A7AE8 | #4A94F2 | 1735400 |
| Light Blue | #EAF3FF | #2A3A4F | 15397887 |

### UI Colors
| Element | Light | Dark |
|---------|-------|------|
| Background | #FFFFFF | #1E1E1E |
| Surface | #FAFAFA | #252525 |
| Border | #E0E0E0 | #3D3D3D |
| Text Primary | #333333 | #E0E0E0 |
| Text Secondary | #666666 | #A0A0A0 |

## Installation

1. Copy XCU files to: `core/officecfg/registry/data/org/openoffice/Office/`
2. Restart PreOffice
3. Access via: Tools > Options > View > Application Colors

## Switching Themes

Users can switch themes via:
- Tools > Options > View > Icon Theme
- Application Colors dropdown in View settings
- System preference detection (when FollowSystem = true)
