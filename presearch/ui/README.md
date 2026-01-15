# PreOffice UI Customizations

This directory contains UI customizations for PreOffice.

## Structure

```
ui/
├── notebookbar/           # Custom Notebookbar presets
│   ├── writer/            # Writer-specific
│   ├── calc/              # Calc-specific
│   └── impress/           # Impress-specific
├── icon-theme/            # Modern flat icons
├── color-scheme/          # Presearch color theme
├── defaults/              # Default settings
└── startcenter/           # Start Center customization
```

## Notebookbar Tabs

PreOffice uses a simplified Notebookbar layout:

### Writer
- **Home**: Common formatting (Bold, Italic, Font, Size, Color, Align)
- **Insert**: Tables, Images, Links, Charts
- **Review**: Spelling, Comments, Track Changes
- **PreSearch**: Search, Ask PreGPT, Privacy Check, Export

### Calc
- **Home**: Cell formatting, Number formats
- **Data**: Sort, Filter, Pivot Tables
- **Formulas**: Functions, Named Ranges
- **PreSearch**: Same as Writer

### Impress
- **Home**: Slide layout, Text formatting
- **Insert**: Media, Shapes, Charts
- **Transitions**: Slide transitions, Animations
- **PreSearch**: Same as Writer

## Color Scheme

Presearch Blue theme:
- Primary: `#2D8EFF`
- Accent: `#1A7AE8`
- Background: `#FFFFFF`
- Surface: `#FAFBFC`
- Tint: `#EAF3FF`

## Applying Customizations

```bash
./apply-ui.sh
```
