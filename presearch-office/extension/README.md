# Presearch Tools Extension

A LibreOffice extension that integrates Presearch services directly into your documents.

## Features

### 1. Search with Presearch
Select any text and search it using Presearch's private search engine.

### 2. Ask PreGPT
Get AI-powered answers about selected text via PreGPT.

### 3. Privacy Check
Scan your document for privacy-sensitive information:
- Author metadata
- Last modified by
- Creation/modification dates
- Comments and annotations
- Tracked changes (redlines)
- Embedded hyperlinks

### 4. Export to PreStorage
Export your document to PDF with optional upload to PreStorage (coming soon).

## Installation

### From Pre-built Package
1. Download `presearch-tools.oxt` from the dist folder
2. Open LibreOffice
3. Go to Tools → Extension Manager
4. Click "Add" and select the .oxt file
5. Restart LibreOffice

### Building from Source
```bash
./build.sh
```

The output will be in `dist/presearch-tools-X.X.X.oxt`

## Usage

After installation, you'll find:
- **Menu**: A new "Presearch" menu in the menu bar
- **Toolbar**: Presearch Tools toolbar buttons

### Keyboard Shortcuts (Optional)
You can assign keyboard shortcuts via:
Tools → Customize → Keyboard

## Configuration

Edit `python/presearch_tools.py` to change:
- `presearch_url`: Search endpoint
- `pregpt_url`: PreGPT endpoint
- `prestorage_enabled`: Enable/disable cloud storage
- `prestorage_endpoint`: Storage API endpoint

## Supported Applications

- Writer (Text Documents)
- Calc (Spreadsheets)
- Impress (Presentations)

## Requirements

- LibreOffice 4.1 or later
- Python support enabled in LibreOffice

## Development

### Directory Structure
```
extension/
  src/
    META-INF/
      manifest.xml      # Extension manifest
    python/
      presearch_tools.py  # Main Python module
    description/
      description-en.txt
    icons/              # Extension icons
    templates/          # Document templates
    config/             # Configuration files
    description.xml     # Extension description
    Addons.xcu          # Menu/toolbar definitions
    LICENSE.txt
  dist/                 # Built .oxt files
  build/                # Temporary build files
  build.sh              # Build script
  README.md
```

### Adding New Commands

1. Create a new class in `presearch_tools.py`:
```python
class MyNewCommand:
    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, args):
        # Your implementation
        pass
```

2. Register it with UNO:
```python
g_ImplementationHelper.addImplementation(
    MyNewCommand,
    "com.presearch.tools.MyNewCommand",
    ("com.sun.star.task.Job",)
)
```

3. Add menu/toolbar entry in `Addons.xcu`

## License

MIT License - see LICENSE.txt
