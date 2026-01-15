/**
 * PreOffice WOPI Server
 * Bridges Collabora Online with PreDrive cloud storage
 *
 * WOPI (Web Application Open Platform Interface) Protocol Implementation
 * https://docs.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/rest/
 */

require('dotenv').config();
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const morgan = require('morgan');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Persistent storage directory
const STORAGE_DIR = process.env.STORAGE_DIR || '/data/preoffice-files';

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_DIR)) {
  fs.mkdirSync(STORAGE_DIR, { recursive: true });
  console.log(`Created storage directory: ${STORAGE_DIR}`);
}

const app = express();
const PORT = process.env.PORT || 8080;

// Configuration
// Note: wopiBaseUrl uses host.docker.internal so Collabora container can reach it
const config = {
  predriveApiUrl: process.env.PREDRIVE_API_URL || 'https://predrive.eu/api',
  wopiBaseUrl: process.env.WOPI_BASE_URL || 'http://host.docker.internal:8080/wopi',
  collaboraUrl: process.env.COLLABORA_URL || 'http://collabora:9980',
  collaboraPublicUrl: process.env.COLLABORA_PUBLIC_URL || 'http://localhost:8000',
  jwtSecret: process.env.JWT_SECRET || 'change-this-secret-in-production',
  tokenExpiry: '24h'
};

// Middleware
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.raw({ type: 'application/octet-stream', limit: '100mb' }));

// In-memory file locks (use Redis in production)
const fileLocks = new Map();

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Generate access token for WOPI operations
 */
function generateAccessToken(userId, fileId) {
  return jwt.sign(
    { userId, fileId, sessionId: uuidv4() },
    config.jwtSecret,
    { expiresIn: config.tokenExpiry }
  );
}

/**
 * Verify access token
 */
function verifyAccessToken(token) {
  try {
    return jwt.verify(token, config.jwtSecret);
  } catch (err) {
    return null;
  }
}

/**
 * Extract access token from request
 */
function getAccessToken(req) {
  return req.query.access_token || req.headers['x-wopi-access-token'];
}

/**
 * Make authenticated request to PreDrive API
 */
async function predriveRequest(method, path, userToken, data = null) {
  const url = `${config.predriveApiUrl}${path}`;
  const headers = {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': 'application/json'
  };

  try {
    const response = await axios({
      method,
      url,
      headers,
      data,
      responseType: path.includes('/content') ? 'arraybuffer' : 'json'
    });
    return response;
  } catch (error) {
    console.error(`PreDrive API error: ${error.message}`);
    throw error;
  }
}

/**
 * Get file extension and determine document type
 */
function getDocumentType(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  const types = {
    // Writer
    odt: 'writer', doc: 'writer', docx: 'writer', rtf: 'writer', txt: 'writer',
    // Calc
    ods: 'calc', xls: 'calc', xlsx: 'calc', csv: 'calc',
    // Impress
    odp: 'impress', ppt: 'impress', pptx: 'impress',
    // Draw
    odg: 'draw',
    // Other
    pdf: 'pdf'
  };
  return types[ext] || 'writer';
}

// =============================================================================
// Authentication Middleware
// =============================================================================

function requireAuth(req, res, next) {
  const token = getAccessToken(req);
  if (!token) {
    return res.status(401).json({ error: 'Access token required' });
  }

  const decoded = verifyAccessToken(token);
  if (!decoded) {
    return res.status(401).json({ error: 'Invalid or expired token' });
  }

  req.auth = decoded;
  next();
}

// =============================================================================
// WOPI Discovery Endpoint
// =============================================================================

app.get('/hosting/discovery', async (req, res) => {
  // Return WOPI discovery XML pointing to Collabora
  try {
    const response = await axios.get(`${config.collaboraUrl}/hosting/discovery`);
    res.type('application/xml').send(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch discovery' });
  }
});

// =============================================================================
// WOPI File Operations
// =============================================================================

// Persistent file storage helpers
function getStoragePath(fileId) {
  // Sanitize fileId for filesystem
  const safeId = fileId.replace(/[^a-zA-Z0-9_-]/g, '_');
  return path.join(STORAGE_DIR, safeId);
}

function readFileFromStorage(fileId) {
  const filePath = getStoragePath(fileId);
  if (fs.existsSync(filePath)) {
    return fs.readFileSync(filePath);
  }
  return null;
}

function writeFileToStorage(fileId, content) {
  const filePath = getStoragePath(fileId);
  fs.writeFileSync(filePath, content);
  console.log(`Saved file to persistent storage: ${filePath} (${content.length} bytes)`);
}

function fileExistsInStorage(fileId) {
  return fs.existsSync(getStoragePath(fileId));
}

// Legacy in-memory fallback (kept for compatibility)
const demoFiles = new Map();

/**
 * CheckFileInfo - Get file metadata
 * GET /wopi/files/{fileId}
 */
app.get('/wopi/files/:fileId', requireAuth, async (req, res) => {
  const { fileId } = req.params;
  const { userId } = req.auth;

  try {
    // Decode fileId (base64 encoded path)
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    const fileName = filePath.split('/').pop();

    // Demo mode: return mock file info for local testing
    console.log(`CheckFileInfo for: ${filePath} (fileId: ${fileId})`);

    // Return WOPI CheckFileInfo response
    res.json({
      BaseFileName: fileName,
      OwnerId: userId,
      Size: fileExistsInStorage(fileId) ? readFileFromStorage(fileId).length : 0,
      UserId: userId,
      Version: Date.now().toString(),

      // Permissions
      UserCanWrite: true,
      UserCanNotWriteRelative: false,
      SupportsUpdate: true,
      SupportsLocks: true,
      SupportsGetLock: true,
      SupportsExtendedLockLength: true,
      SupportsCobalt: false,
      SupportsFolders: false,
      SupportsDeleteFile: true,
      SupportsRename: true,

      // User info
      UserFriendlyName: 'Demo User',
      IsAnonymousUser: false,

      // Branding
      BreadcrumbBrandName: 'PreOffice',
      BreadcrumbBrandUrl: 'http://localhost:8000',
      BreadcrumbFolderName: filePath.split('/').slice(0, -1).join('/') || '/',
      BreadcrumbFolderUrl: 'http://localhost:8000',

      // Features
      DisablePrint: false,
      DisableExport: false,
      DisableCopy: false,
      EnableOwnerTermination: true,

      // PostMessage
      PostMessageOrigin: 'http://localhost:8000',

      // Last modified
      LastModifiedTime: new Date().toISOString()
    });
  } catch (error) {
    console.error('CheckFileInfo error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

/**
 * GetFile - Download file contents
 * GET /wopi/files/{fileId}/contents
 */
app.get('/wopi/files/:fileId/contents', requireAuth, async (req, res) => {
  const { fileId } = req.params;

  try {
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    console.log(`GetFile for: ${filePath} (fileId: ${fileId})`);

    // Try persistent storage first
    const storedContent = readFileFromStorage(fileId);
    if (storedContent) {
      console.log(`Returning persistent file content (${storedContent.length} bytes)`);
      res.set('Content-Type', 'application/octet-stream');
      return res.send(storedContent);
    }

    // Fall back to in-memory storage
    if (demoFiles.has(fileId)) {
      console.log(`Returning in-memory file content (${demoFiles.get(fileId).length} bytes)`);
      res.set('Content-Type', 'application/octet-stream');
      return res.send(demoFiles.get(fileId));
    }

    // For new files, return empty content (Collabora will create new document)
    console.log('No file found, returning empty content for new document');
    res.set('Content-Type', 'application/octet-stream');
    res.send(Buffer.alloc(0));
  } catch (error) {
    console.error('GetFile error:', error.message);
    res.status(404).json({ error: 'File not found' });
  }
});

/**
 * PutFile - Upload/save file contents
 * POST /wopi/files/{fileId}/contents
 */
app.post('/wopi/files/:fileId/contents', requireAuth, async (req, res) => {
  const { fileId } = req.params;
  const lockId = req.headers['x-wopi-lock'];

  try {
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    console.log(`PutFile for: ${filePath} (fileId: ${fileId})`);

    // Check lock
    const currentLock = fileLocks.get(fileId);
    if (currentLock && currentLock !== lockId) {
      res.set('X-WOPI-Lock', currentLock);
      return res.status(409).json({ error: 'File is locked' });
    }

    // Store to persistent storage
    const content = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body);
    writeFileToStorage(fileId, content);
    // Also keep in memory for faster subsequent reads
    demoFiles.set(fileId, content);

    res.json({
      ItemVersion: Date.now().toString()
    });
  } catch (error) {
    console.error('PutFile error:', error.message);
    res.status(500).json({ error: 'Failed to save file' });
  }
});

/**
 * Lock/Unlock operations
 * POST /wopi/files/{fileId}
 */
app.post('/wopi/files/:fileId', requireAuth, async (req, res) => {
  const { fileId } = req.params;
  const override = req.headers['x-wopi-override'];
  const lockId = req.headers['x-wopi-lock'];
  const oldLockId = req.headers['x-wopi-oldlock'];

  const currentLock = fileLocks.get(fileId);

  switch (override) {
    case 'LOCK':
      if (currentLock && currentLock !== lockId) {
        res.set('X-WOPI-Lock', currentLock);
        return res.status(409).json({ error: 'File already locked' });
      }
      fileLocks.set(fileId, lockId);
      res.set('X-WOPI-ItemVersion', Date.now().toString());
      return res.status(200).end();

    case 'GET_LOCK':
      res.set('X-WOPI-Lock', currentLock || '');
      return res.status(200).end();

    case 'REFRESH_LOCK':
      if (currentLock !== lockId) {
        res.set('X-WOPI-Lock', currentLock || '');
        return res.status(409).json({ error: 'Lock mismatch' });
      }
      // Refresh the lock (just update timestamp in production)
      return res.status(200).end();

    case 'UNLOCK':
      if (currentLock !== lockId) {
        res.set('X-WOPI-Lock', currentLock || '');
        return res.status(409).json({ error: 'Lock mismatch' });
      }
      fileLocks.delete(fileId);
      return res.status(200).end();

    case 'UNLOCK_AND_RELOCK':
      if (currentLock !== oldLockId) {
        res.set('X-WOPI-Lock', currentLock || '');
        return res.status(409).json({ error: 'Lock mismatch' });
      }
      fileLocks.set(fileId, lockId);
      return res.status(200).end();

    case 'PUT_RELATIVE':
      // Create new file with suggested name
      const suggestedName = req.headers['x-wopi-suggestedtarget'];
      const relativeName = req.headers['x-wopi-relativetarget'];
      // Implementation depends on PreDrive API
      return res.status(501).json({ error: 'Not implemented' });

    case 'RENAME_FILE':
      const newName = req.headers['x-wopi-requestedname'];
      // Implementation depends on PreDrive API
      return res.status(501).json({ error: 'Not implemented' });

    case 'DELETE':
      if (currentLock && currentLock !== lockId) {
        res.set('X-WOPI-Lock', currentLock);
        return res.status(409).json({ error: 'File is locked' });
      }
      // Implementation depends on PreDrive API
      return res.status(501).json({ error: 'Not implemented' });

    default:
      return res.status(400).json({ error: 'Unknown operation' });
  }
});

// =============================================================================
// PreOffice Online Frontend Endpoints
// =============================================================================

/**
 * Get editor URL for a file
 * Returns the URL to open in iframe/new tab
 */
app.post('/api/edit', async (req, res) => {
  const { filePath, userToken, userId, userName } = req.body;

  if (!filePath || !userToken) {
    return res.status(400).json({ error: 'filePath and userToken required' });
  }

  try {
    // Generate file ID (base64 encoded path)
    const fileId = Buffer.from(filePath).toString('base64');

    // Generate WOPI access token
    const accessToken = generateAccessToken(userId || 'anonymous', fileId);

    // Store user token for later PreDrive API calls
    // In production, use Redis or similar
    const sessionData = verifyAccessToken(accessToken);
    sessionData.userToken = userToken;

    // Get file extension to determine editor
    const ext = filePath.split('.').pop().toLowerCase();

    // Determine Collabora editor action
    let action = 'edit';
    if (['pdf'].includes(ext)) {
      action = 'view';
    }

    // Build Collabora URL (use public URL for browser access)
    const wopiSrc = encodeURIComponent(`${config.wopiBaseUrl}/files/${fileId}`);
    const collaboraEditorUrl = `${config.collaboraPublicUrl}/browser/dist/cool.html?WOPISrc=${wopiSrc}&access_token=${accessToken}`;

    res.json({
      editorUrl: collaboraEditorUrl,
      fileId,
      accessToken,
      expiresIn: config.tokenExpiry
    });
  } catch (error) {
    console.error('Edit endpoint error:', error.message);
    res.status(500).json({ error: 'Failed to generate editor URL' });
  }
});

/**
 * Create new document
 */
app.post('/api/create', async (req, res) => {
  const { type, folder, name, userToken, userId } = req.body;

  const templates = {
    document: { ext: 'odt', template: 'empty.odt' },
    spreadsheet: { ext: 'ods', template: 'empty.ods' },
    presentation: { ext: 'odp', template: 'empty.odp' },
    drawing: { ext: 'odg', template: 'empty.odg' }
  };

  const docType = templates[type] || templates.document;
  const fileName = name || `Untitled.${docType.ext}`;
  const filePath = `${folder || '/'}/${fileName}`.replace('//', '/');

  try {
    // Create empty file in PreDrive
    // This would call PreDrive API to create the file

    // For now, return the edit URL
    const fileId = Buffer.from(filePath).toString('base64');
    const accessToken = generateAccessToken(userId || 'anonymous', fileId);

    const wopiSrc = encodeURIComponent(`${config.wopiBaseUrl}/files/${fileId}`);
    const collaboraEditorUrl = `${config.collaboraPublicUrl}/browser/dist/cool.html?WOPISrc=${wopiSrc}&access_token=${accessToken}`;

    res.json({
      filePath,
      editorUrl: collaboraEditorUrl,
      fileId,
      accessToken
    });
  } catch (error) {
    res.status(500).json({ error: 'Failed to create document' });
  }
});

/**
 * Health check
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'PreOffice WOPI Server',
    version: '1.0.0',
    collabora: config.collaboraPublicUrl,
    predrive: config.predriveApiUrl
  });
});

// =============================================================================
// Start Server
// =============================================================================

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║           PreOffice Online - WOPI Server                  ║
╠═══════════════════════════════════════════════════════════╣
║  Port:        ${PORT}                                         ║
║  PreDrive:    ${config.predriveApiUrl.padEnd(35)}     ║
║  Collabora:   ${config.collaboraUrl.padEnd(35)}     ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;
