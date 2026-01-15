# PrePanda AI Writing Assistant

PrePanda is the AI-powered writing assistant for PreOffice, part of the Presearch Pre-suite.
It uses Venice.ai's API to provide intelligent writing assistance directly in your documents.

## Features

- **Summarize** - Get concise summaries of selected text
- **Improve** - Enhance writing quality and clarity
- **Translate** - Translate to multiple languages
- **Explain** - Get simple explanations of complex text
- **Proofread** - Check grammar and spelling
- **Expand** - Add more detail to your content
- **Ask** - Ask any question with document context

## Architecture

```
ai-assistant/
├── css/
│   └── prepanda.css          # UI styling (Presearch theme)
├── js/
│   └── prepanda.js           # Frontend chat component
├── python/
│   ├── prepanda_service.py   # Venice.ai API integration
│   └── prepanda_extension.py # LibreOffice UNO extension
├── config/
│   └── prepanda.json         # Configuration file
└── prepanda-panel.html       # Sidebar panel template
```

## Setup

### 1. Get Venice.ai API Key

1. Visit [Venice.ai](https://venice.ai)
2. Create an account and get an API key
3. Set the environment variable:

```bash
export VENICE_API_KEY="your-api-key-here"
```

Or add to your shell profile (~/.bashrc, ~/.zshrc):

```bash
echo 'export VENICE_API_KEY="your-api-key"' >> ~/.zshrc
```

### 2. Install in PreOffice

The AI assistant is automatically installed with PreOffice customizations:

```bash
cd presearch
./install.sh
```

### 3. Access PrePanda

- **Menu**: Tools > PrePanda AI Assistant
- **Keyboard**: Ctrl+Shift+P (customizable)
- **Context Menu**: Right-click selected text > PrePanda

## Configuration

Edit `config/prepanda.json` to customize:

```json
{
  "api": {
    "url": "https://api.venice.ai/api/v1",
    "models": {
      "ask_balanced": "llama-3.3-70b"
    }
  },
  "settings": {
    "response_style": "concise",
    "dark_mode": false
  }
}
```

## API Models

| Model | Use Case | Speed | Quality |
|-------|----------|-------|---------|
| llama-3.2-3b | Quick summaries | Fast | Good |
| llama-3.3-70b | Detailed answers | Medium | Better |

## Styling

The UI follows Presearch design guidelines:

| Element | Color |
|---------|-------|
| Primary | #2D8EFF (Presearch Blue) |
| Primary Dark | #1A7AE8 |
| Primary Light | #5BA3FF |
| Background | #FFFFFF |
| Text | #333333 |

## Privacy

- **No data stored** - Conversations are not saved by default
- **Local processing** - Document context stays on your machine
- **Anonymous** - No user tracking or profiling
- **Open source** - Full transparency

## Development

### Testing the Service

```bash
# Test the Python service directly
python python/prepanda_service.py summarize "Your text here"

# Interactive mode
python python/prepanda_service.py ask
```

### Testing the UI

Open `prepanda-panel.html` in a browser with API key:

```
prepanda-panel.html?apiKey=your-key-here
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+Shift+P | Open PrePanda |
| Ctrl+Shift+S | Summarize selection |
| Ctrl+Shift+I | Improve selection |
| Ctrl+Shift+T | Translate selection |

## Troubleshooting

### "API key not configured"

Set the `VENICE_API_KEY` environment variable.

### "Network error"

Check your internet connection and Venice.ai API status.

### "PrePanda service not available"

Ensure Python dependencies are installed and the extension is loaded.

## Credits

- **Design**: Based on Presearch PreGPT UI
- **API**: Powered by Venice.ai
- **Framework**: LibreOffice UNO
