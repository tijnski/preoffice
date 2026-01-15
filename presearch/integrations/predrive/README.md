# PreDrive Integration for PreOffice

Cloud storage integration extension that connects PreOffice to PreDrive.

## Features

- **Open from PreDrive** - Browse and open documents stored in PreDrive
- **Save to PreDrive** - Save documents directly to your PreDrive storage
- **File Browser** - Navigate folders, create new folders
- **Automatic Versioning** - PreDrive keeps version history of your documents
- **WebDAV Support** - Native WebDAV integration for seamless editing

## Installation

### From OXT Package

1. Build the extension: `./build.sh`
2. Open PreOffice/LibreOffice
3. Go to **Tools > Extension Manager**
4. Click **Add** and select `dist/predrive-1.0.0.oxt`
5. Restart PreOffice

### Manual Installation (Development)

Copy the extension directory to your LibreOffice user extensions folder:

```bash
# macOS
cp -r predrive ~/Library/Application\ Support/LibreOffice/4/user/extensions/

# Linux
cp -r predrive ~/.config/libreoffice/4/user/extensions/

# Windows
copy predrive %APPDATA%\LibreOffice\4\user\extensions\
```

## Configuration

### Via Options Dialog

1. Go to **Tools > Options**
2. Navigate to **PreSuite > PreDrive**
3. Enter your PreDrive server URL
4. Enter your authentication credentials

### Via Config File

Edit `~/.config/preoffice/predrive.json`:

```json
{
  "server_url": "https://drive.presearch.com",
  "jwt_token": "your-jwt-token",
  "user_email": "user@example.com",
  "remember_credentials": true
}
```

## Usage

### Save to PreDrive

1. Open a document in PreOffice
2. Go to **PreDrive > Save to PreDrive...**
3. Select destination folder
4. Click **Save**

### Open from PreDrive

1. Go to **PreDrive > Open from PreDrive...**
2. Browse to the file
3. Click **Open**

### WebDAV Access

For direct WebDAV access (allows real-time editing):

1. Go to **File > Open Remote...**
2. Add a new WebDAV service:
   - Server: `your-predrive-server.com`
   - Port: `4000` (or your configured port)
   - Path: `/dav`
3. Use your email as username and JWT token as password

## API Integration

The extension uses PreDrive's REST API:

- `POST /api/nodes/files/upload/start` - Initiate upload
- `POST /api/nodes/files/upload/complete` - Complete upload
- `GET /api/nodes/files/:id/download` - Get download URL
- `GET /api/nodes` - List files and folders
- `POST /api/nodes/folders` - Create folder

## Development

### Project Structure

```
predrive/
├── META-INF/
│   └── manifest.xml      # Extension manifest
├── python/
│   └── predrive.py       # Main Python component
├── dialogs/
│   ├── LoginDialog.xdl   # Login dialog
│   ├── FileBrowser.xdl   # File browser dialog
│   ├── SaveDialog.xdl    # Save dialog
│   └── PreDriveOptions.xdl # Options page
├── icons/                # Extension icons
├── description/          # Extension descriptions
├── description.xml       # Extension metadata
├── Addons.xcu           # Menu configuration
├── OptionsDialog.xcu    # Options dialog config
├── LICENSE.txt          # License file
└── build.sh             # Build script
```

### Building

```bash
./build.sh
```

This creates `dist/predrive-1.0.0.oxt`.

### Testing

1. Install the extension in PreOffice
2. Ensure PreDrive server is running
3. Configure server URL in extension settings
4. Test save/open operations

## License

MPL-2.0 - See LICENSE.txt

## Credits

Part of the PreSuite ecosystem by Presearch.
