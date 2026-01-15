# PreOffice Online

Web-based document editing powered by Collabora Online, integrated with PreDrive cloud storage.

## Overview

PreOffice Online provides a full-featured office suite in the browser:

- **PreWriter** - Word processing (ODT, DOCX, RTF)
- **PreCalc** - Spreadsheets (ODS, XLSX, CSV)
- **PreImpress** - Presentations (ODP, PPTX)
- **PreDraw** - Diagrams and drawings (ODG)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Nginx                                │
│              (SSL termination, reverse proxy)               │
└──────────────┬───────────────────────┬──────────────────────┘
               │                       │
       ┌───────▼───────┐       ┌───────▼───────┐
       │  WOPI Server  │       │   Collabora   │
       │   (Node.js)   │◄─────►│    Online     │
       └───────┬───────┘       └───────────────┘
               │
       ┌───────▼───────┐
       │   PreDrive    │
       │     API       │
       └───────────────┘
```

### Components

1. **Nginx** - Reverse proxy with SSL termination
2. **WOPI Server** - Bridge between Collabora and PreDrive storage
3. **Collabora Online** - Document editing engine (LibreOffice-based)
4. **Redis** - Session management (optional)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Domain with DNS configured (for production)
- SSL certificates (auto-generated for development)

### Development Setup

```bash
# Clone and navigate to the online directory
cd presearch/online

# Copy environment file
cp .env.example .env

# Start services
./scripts/start.sh
```

### Production Deployment

1. **Configure DNS** - Point your domain to the server

2. **Get SSL certificates** (using Let's Encrypt):
   ```bash
   certbot certonly --standalone -d preoffice.eu
   cp /etc/letsencrypt/live/preoffice.eu/fullchain.pem nginx/ssl/
   cp /etc/letsencrypt/live/preoffice.eu/privkey.pem nginx/ssl/
   ```

3. **Update .env**:
   ```env
   COLLABORA_ADMIN_PASS=<strong-password>
   JWT_SECRET=<random-64-char-string>
   PREDRIVE_API_URL=https://predrive.eu/api
   WOPI_BASE_URL=https://preoffice.eu/wopi
   ```

4. **Start services**:
   ```bash
   docker compose up -d
   ```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `COLLABORA_ADMIN_USER` | Admin console username | `admin` |
| `COLLABORA_ADMIN_PASS` | Admin console password | - |
| `PREDRIVE_API_URL` | PreDrive API endpoint | `https://predrive.eu/api` |
| `WOPI_BASE_URL` | WOPI server base URL | `https://preoffice.eu/wopi` |
| `JWT_SECRET` | Secret for access tokens | - |

### Branding

Customize the look and feel by editing files in `branding/`:

- `static/index.html` - Landing page
- `static/favicon.svg` - Browser icon
- Collabora branding can be configured via environment variables

## API Endpoints

### Create Document
```http
POST /api/create
Content-Type: application/json

{
  "type": "document|spreadsheet|presentation|drawing",
  "name": "My Document.odt",
  "folder": "/",
  "userToken": "<predrive-auth-token>"
}
```

### Edit Document
```http
POST /api/edit
Content-Type: application/json

{
  "filePath": "/Documents/report.odt",
  "userToken": "<predrive-auth-token>",
  "userId": "user123"
}
```

Response:
```json
{
  "editorUrl": "https://preoffice.eu/loleaflet/...",
  "fileId": "...",
  "accessToken": "..."
}
```

### Health Check
```http
GET /health
```

## WOPI Protocol

The WOPI server implements the [WOPI protocol](https://docs.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/rest/) for communication between Collabora and PreDrive:

- `GET /wopi/files/{fileId}` - CheckFileInfo
- `GET /wopi/files/{fileId}/contents` - GetFile
- `POST /wopi/files/{fileId}/contents` - PutFile
- `POST /wopi/files/{fileId}` - Lock/Unlock operations

## Troubleshooting

### Services not starting
```bash
# Check logs
docker compose logs -f

# Check individual service
docker compose logs collabora
docker compose logs wopi
```

### Connection issues
```bash
# Test WOPI server
curl http://localhost:8080/health

# Test Collabora
curl http://localhost:9980/hosting/discovery
```

### SSL certificate issues
For development, self-signed certificates are generated automatically.
For production, ensure certificates are valid and properly configured.

## Security Considerations

1. **Always use HTTPS in production**
2. **Use strong, unique passwords** for admin console
3. **Rotate JWT secrets regularly**
4. **Configure allowed domains** in Collabora settings
5. **Set up firewall rules** to restrict direct access to internal services

## Resources

- [Collabora Online Documentation](https://sdk.collaboraonline.com/)
- [WOPI Protocol Reference](https://docs.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/rest/)
- [PreDrive API Documentation](https://predrive.eu/docs)

## License

Copyright (c) 2024 Presearch. Licensed under MPL-2.0.
