/**
 * PreOffice WOPI Server
 * Bridges Collabora Online with PreDrive cloud storage
 *
 * WOPI (Web Application Open Platform Interface) Protocol Implementation
 * https://docs.microsoft.com/en-us/microsoft-365/cloud-storage-partner-program/rest/
 *
 * Security-hardened version with:
 * - Rate limiting
 * - Security headers
 * - Input validation
 * - Secure logging
 * - Proper authentication
 */

require('dotenv').config();
const express = require('express');
const helmet = require('helmet');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// Import security modules
const {
  IS_PRODUCTION,
  JWT_SECRET,
  JWT_TOKEN_EXPIRY,
  SESSION_EXPIRY_MS,
  SESSION_CLEANUP_INTERVAL_MS,
  MAX_FILE_SIZE_BYTES,
  CORS_ALLOWED_ORIGINS
} = require('./config/constants');

const { logger } = require('./utils/logger');
const { securityHeaders, corsMiddleware, validateFileId, sanitizeFilename } = require('./middleware/security');
const { apiRateLimiter, editRateLimiter, createRateLimiterMiddleware, wopiRateLimiter } = require('./middleware/rate-limiter');
const { requireBearerAuth, requireWopiAuth } = require('./middleware/auth');

// Persistent storage directory (fallback for demo mode)
const STORAGE_DIR = process.env.STORAGE_DIR || '/data/preoffice-files';

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_DIR)) {
  fs.mkdirSync(STORAGE_DIR, { recursive: true });
  logger.info('Created storage directory', { path: STORAGE_DIR });
}

const app = express();
const PORT = process.env.PORT || 8080;

// Configuration
const config = {
  predriveApiUrl: process.env.PREDRIVE_API_URL || 'https://predrive.eu/api',
  wopiBaseUrl: process.env.WOPI_BASE_URL || 'http://host.docker.internal:8080/wopi',
  collaboraUrl: process.env.COLLABORA_URL || 'http://collabora:9980',
  collaboraPublicUrl: process.env.COLLABORA_PUBLIC_URL || 'http://localhost:8000',
  jwtSecret: JWT_SECRET,
  tokenExpiry: JWT_TOKEN_EXPIRY,
  usePreDrive: process.env.USE_PREDRIVE === 'true'
};

// =============================================================================
// Middleware Setup
// =============================================================================

// Security headers (using our custom middleware + helmet)
app.use(helmet({
  contentSecurityPolicy: false, // We handle CSP separately for Collabora compatibility
  crossOriginEmbedderPolicy: false, // Required for iframe embedding
  crossOriginOpenerPolicy: false
}));

app.use(securityHeaders);
app.use(corsMiddleware);

// Request parsing with size limits
app.use(express.json({ limit: '1mb' }));
app.use(express.raw({
  type: 'application/octet-stream',
  limit: `${MAX_FILE_SIZE_BYTES}`
}));

// Request logging (secure)
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info('Request completed', {
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: `${duration}ms`
    });
  });
  next();
});

// =============================================================================
// Session Store
// =============================================================================

// In-memory stores (use Redis in production for distributed systems)
const fileLocks = new Map();
const sessionStore = new Map();

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Generate access token for WOPI operations
 * Includes PreDrive node ID and user token for API calls
 */
function generateAccessToken(userId, fileId, nodeId, userToken, userName) {
  const sessionId = uuidv4();
  const token = jwt.sign(
    { userId, fileId, nodeId, sessionId },
    config.jwtSecret,
    { expiresIn: config.tokenExpiry }
  );

  // Store user token and metadata in session store
  sessionStore.set(sessionId, {
    userToken,
    userName: userName || 'User',
    nodeId,
    fileId,
    userId,
    createdAt: Date.now()
  });

  return token;
}

/**
 * Make authenticated request to PreDrive API
 */
async function predriveRequest(method, endpoint, userToken, data = null, options = {}) {
  const url = `${config.predriveApiUrl}${endpoint}`;
  const headers = {
    'Authorization': `Bearer ${userToken}`,
    'Content-Type': options.contentType || 'application/json'
  };

  try {
    const response = await axios({
      method,
      url,
      headers,
      data,
      responseType: options.responseType || 'json',
      maxContentLength: MAX_FILE_SIZE_BYTES,
      maxBodyLength: MAX_FILE_SIZE_BYTES,
      timeout: 30000
    });
    return response;
  } catch (error) {
    logger.error('PreDrive API error', {
      method,
      endpoint,
      error: error.message
    });
    throw error;
  }
}

/**
 * Download file content from PreDrive
 */
async function downloadFromPreDrive(nodeId, userToken) {
  try {
    const response = await predriveRequest('GET', `/nodes/files/${nodeId}/download`, userToken);
    const downloadUrl = response.data.downloadUrl;

    if (!downloadUrl) {
      throw new Error('No download URL returned from PreDrive');
    }

    const fileResponse = await axios.get(downloadUrl, {
      responseType: 'arraybuffer',
      maxContentLength: MAX_FILE_SIZE_BYTES,
      timeout: 60000
    });

    return Buffer.from(fileResponse.data);
  } catch (error) {
    logger.error('Failed to download from PreDrive', { nodeId, error: error.message });
    throw error;
  }
}

/**
 * Upload file content to PreDrive
 */
async function uploadToPreDrive(nodeId, content, fileName, userToken) {
  try {
    const mime = getMimeType(fileName);

    const response = await axios.put(
      `${config.predriveApiUrl}/nodes/files/${nodeId}/content`,
      content,
      {
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': mime,
          'Content-Length': content.length
        },
        maxContentLength: MAX_FILE_SIZE_BYTES,
        maxBodyLength: MAX_FILE_SIZE_BYTES,
        timeout: 60000
      }
    );

    return response.data;
  } catch (error) {
    logger.error('Failed to upload to PreDrive', { nodeId, error: error.message });
    throw error;
  }
}

/**
 * Get MIME type from filename
 */
function getMimeType(filename) {
  const ext = (filename || '').split('.').pop().toLowerCase();
  const mimeTypes = {
    odt: 'application/vnd.oasis.opendocument.text',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    rtf: 'application/rtf',
    txt: 'text/plain',
    ods: 'application/vnd.oasis.opendocument.spreadsheet',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    csv: 'text/csv',
    odp: 'application/vnd.oasis.opendocument.presentation',
    ppt: 'application/vnd.ms-powerpoint',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    odg: 'application/vnd.oasis.opendocument.graphics',
    pdf: 'application/pdf'
  };
  return mimeTypes[ext] || 'application/octet-stream';
}

/**
 * Get document type for Collabora
 */
function getDocumentType(filename) {
  const ext = (filename || '').split('.').pop().toLowerCase();
  const types = {
    odt: 'writer', doc: 'writer', docx: 'writer', rtf: 'writer', txt: 'writer',
    ods: 'calc', xls: 'calc', xlsx: 'calc', csv: 'calc',
    odp: 'impress', ppt: 'impress', pptx: 'impress',
    odg: 'draw',
    pdf: 'pdf'
  };
  return types[ext] || 'writer';
}

// =============================================================================
// Local Storage Fallback (Demo Mode)
// =============================================================================

function getStoragePath(fileId) {
  // Sanitize fileId to prevent path traversal
  const safeId = fileId.replace(/[^a-zA-Z0-9_=-]/g, '_').substring(0, 100);
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
  logger.info('Saved file to storage', { size: content.length });
}

function fileExistsInStorage(fileId) {
  return fs.existsSync(getStoragePath(fileId));
}

const demoFiles = new Map();

// =============================================================================
// WOPI Discovery Endpoint
// =============================================================================

app.get('/hosting/discovery', async (req, res) => {
  try {
    const response = await axios.get(`${config.collaboraUrl}/hosting/discovery`, {
      timeout: 10000
    });
    res.type('application/xml').send(response.data);
  } catch (error) {
    logger.error('Failed to fetch discovery', { error: error.message });
    res.status(500).json({ error: 'Failed to fetch discovery' });
  }
});

// =============================================================================
// WOPI File Operations
// =============================================================================

const wopiAuth = requireWopiAuth(sessionStore);

/**
 * CheckFileInfo - Get file metadata
 * GET /wopi/files/{fileId}
 */
app.get('/wopi/files/:fileId', wopiRateLimiter, wopiAuth, async (req, res) => {
  const { fileId } = req.params;
  const { userId, nodeId, session } = req.auth;

  // Validate fileId
  const validation = validateFileId(fileId);
  if (!validation.valid) {
    return res.status(400).json({ error: validation.error });
  }

  try {
    const fileName = validation.path.split('/').pop();
    logger.debug('CheckFileInfo', { nodeId });

    let fileSize = 0;
    let lastModified = new Date();
    let userName = session?.userName || 'User';
    let version = Date.now().toString();

    if (config.usePreDrive && nodeId && session?.userToken) {
      try {
        const nodeResponse = await predriveRequest('GET', `/nodes/${nodeId}`, session.userToken);
        const node = nodeResponse.data;
        fileSize = node.file?.size || 0;
        lastModified = new Date(node.updatedAt || node.createdAt);
        version = node.file?.currentVersion?.toString() || version;
      } catch (error) {
        logger.debug('PreDrive lookup failed, using defaults');
      }
    } else {
      if (fileExistsInStorage(fileId)) {
        fileSize = readFileFromStorage(fileId).length;
      }
    }

    res.json({
      BaseFileName: fileName,
      OwnerId: userId,
      Size: fileSize,
      UserId: userId,
      Version: version,
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
      UserFriendlyName: userName,
      IsAnonymousUser: false,
      BreadcrumbBrandName: 'PreOffice',
      BreadcrumbBrandUrl: config.collaboraPublicUrl,
      BreadcrumbFolderName: validation.path.split('/').slice(0, -1).join('/') || '/',
      BreadcrumbFolderUrl: config.collaboraPublicUrl,
      DisablePrint: false,
      DisableExport: false,
      DisableCopy: false,
      EnableOwnerTermination: true,
      PostMessageOrigin: config.collaboraPublicUrl,
      LastModifiedTime: lastModified.toISOString()
    });
  } catch (error) {
    logger.error('CheckFileInfo error', { error: error.message });
    res.status(500).json({ error: 'Internal server error' });
  }
});

/**
 * GetFile - Download file contents
 * GET /wopi/files/{fileId}/contents
 */
app.get('/wopi/files/:fileId/contents', wopiRateLimiter, wopiAuth, async (req, res) => {
  const { fileId } = req.params;
  const { nodeId, session } = req.auth;

  const validation = validateFileId(fileId);
  if (!validation.valid) {
    return res.status(400).json({ error: validation.error });
  }

  try {
    logger.debug('GetFile', { nodeId });

    if (config.usePreDrive && nodeId && session?.userToken) {
      try {
        const content = await downloadFromPreDrive(nodeId, session.userToken);
        logger.debug('Returning PreDrive content', { size: content.length });
        res.set('Content-Type', 'application/octet-stream');
        return res.send(content);
      } catch (error) {
        logger.debug('PreDrive download failed, trying local storage');
      }
    }

    const storedContent = readFileFromStorage(fileId);
    if (storedContent) {
      res.set('Content-Type', 'application/octet-stream');
      return res.send(storedContent);
    }

    if (demoFiles.has(fileId)) {
      res.set('Content-Type', 'application/octet-stream');
      return res.send(demoFiles.get(fileId));
    }

    logger.debug('No file found, returning empty content');
    res.set('Content-Type', 'application/octet-stream');
    res.send(Buffer.alloc(0));
  } catch (error) {
    logger.error('GetFile error', { error: error.message });
    res.status(404).json({ error: 'File not found' });
  }
});

/**
 * PutFile - Upload/save file contents
 * POST /wopi/files/{fileId}/contents
 */
app.post('/wopi/files/:fileId/contents', wopiRateLimiter, wopiAuth, async (req, res) => {
  const { fileId } = req.params;
  const { nodeId, session } = req.auth;
  const lockId = req.headers['x-wopi-lock'];

  const validation = validateFileId(fileId);
  if (!validation.valid) {
    return res.status(400).json({ error: validation.error });
  }

  try {
    const fileName = validation.path.split('/').pop();
    logger.debug('PutFile', { nodeId });

    const currentLock = fileLocks.get(fileId);
    if (currentLock && currentLock !== lockId) {
      res.set('X-WOPI-Lock', currentLock);
      return res.status(409).json({ error: 'File is locked' });
    }

    const content = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body);
    let newVersion = Date.now().toString();

    if (config.usePreDrive && nodeId && session?.userToken) {
      try {
        const result = await uploadToPreDrive(nodeId, content, fileName, session.userToken);
        newVersion = result.version?.toString() || newVersion;
        logger.info('Saved to PreDrive', { size: content.length, version: newVersion });
      } catch (error) {
        logger.warn('PreDrive upload failed, saving to local storage');
        writeFileToStorage(fileId, content);
        demoFiles.set(fileId, content);
      }
    } else {
      writeFileToStorage(fileId, content);
      demoFiles.set(fileId, content);
    }

    res.json({ ItemVersion: newVersion });
  } catch (error) {
    logger.error('PutFile error', { error: error.message });
    res.status(500).json({ error: 'Failed to save file' });
  }
});

/**
 * Lock/Unlock operations
 * POST /wopi/files/{fileId}
 */
app.post('/wopi/files/:fileId', wopiRateLimiter, wopiAuth, async (req, res) => {
  const { fileId } = req.params;
  const { nodeId, session } = req.auth;
  const override = req.headers['x-wopi-override'];
  const lockId = req.headers['x-wopi-lock'];
  const oldLockId = req.headers['x-wopi-oldlock'];

  const validation = validateFileId(fileId);
  if (!validation.valid) {
    return res.status(400).json({ error: validation.error });
  }

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
      return handlePutRelative(req, res, fileId, session, validation.path);

    case 'RENAME_FILE':
      return handleRenameFile(req, res, fileId, nodeId, session);

    case 'DELETE':
      return handleDeleteFile(req, res, fileId, nodeId, lockId, currentLock, session);

    default:
      return res.status(400).json({ error: 'Unknown operation' });
  }
});

/**
 * Handle PUT_RELATIVE
 */
async function handlePutRelative(req, res, fileId, session, filePath) {
  const suggestedName = req.headers['x-wopi-suggestedtarget'];
  const relativeName = req.headers['x-wopi-relativetarget'];

  if (!config.usePreDrive || !session?.userToken) {
    return res.status(501).json({ error: 'PreDrive integration not configured' });
  }

  try {
    const folderPath = filePath.split('/').slice(0, -1).join('/') || '/';

    let newFileName = relativeName || suggestedName;
    newFileName = sanitizeFilename(newFileName);

    if (!newFileName) {
      return res.status(400).json({ error: 'Invalid filename' });
    }

    if (newFileName.startsWith('.')) {
      const baseName = filePath.split('/').pop().split('.').slice(0, -1).join('.');
      newFileName = baseName + newFileName;
    }

    const newFilePath = `${folderPath}/${newFileName}`.replace('//', '/');
    const newFileId = Buffer.from(newFilePath).toString('base64');

    const content = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body || '');
    writeFileToStorage(newFileId, content);
    demoFiles.set(newFileId, content);

    const newAccessToken = generateAccessToken(
      session.userId,
      newFileId,
      null,
      session.userToken,
      session.userName
    );

    res.json({
      Name: newFileName,
      Url: `${config.wopiBaseUrl}/files/${newFileId}?access_token=${newAccessToken}`
    });
  } catch (error) {
    logger.error('PUT_RELATIVE error', { error: error.message });
    res.status(500).json({ error: 'Failed to create file' });
  }
}

/**
 * Handle RENAME_FILE
 */
async function handleRenameFile(req, res, fileId, nodeId, session) {
  const newName = req.headers['x-wopi-requestedname'];

  const sanitizedName = sanitizeFilename(newName);
  if (!sanitizedName) {
    return res.status(400).json({ error: 'Invalid filename' });
  }

  if (!config.usePreDrive || !nodeId || !session?.userToken) {
    return res.json({ Name: sanitizedName });
  }

  try {
    await predriveRequest('PATCH', `/nodes/${nodeId}`, session.userToken, {
      name: sanitizedName
    });

    res.json({ Name: sanitizedName });
  } catch (error) {
    logger.error('RENAME_FILE error', { error: error.message });
    res.status(500).json({ error: 'Failed to rename file' });
  }
}

/**
 * Handle DELETE
 */
async function handleDeleteFile(req, res, fileId, nodeId, lockId, currentLock, session) {
  if (currentLock && currentLock !== lockId) {
    res.set('X-WOPI-Lock', currentLock);
    return res.status(409).json({ error: 'File is locked' });
  }

  if (!config.usePreDrive || !nodeId || !session?.userToken) {
    const storagePath = getStoragePath(fileId);
    if (fs.existsSync(storagePath)) {
      fs.unlinkSync(storagePath);
    }
    demoFiles.delete(fileId);
    fileLocks.delete(fileId);
    return res.status(200).end();
  }

  try {
    await predriveRequest('DELETE', `/nodes/${nodeId}`, session.userToken);
    fileLocks.delete(fileId);
    res.status(200).end();
  } catch (error) {
    logger.error('DELETE error', { error: error.message });
    res.status(500).json({ error: 'Failed to delete file' });
  }
}

// =============================================================================
// PreOffice API Endpoints (with authentication)
// =============================================================================

/**
 * OAuth token exchange endpoint
 * POST /api/oauth/token
 * This handles the token exchange on the server side to keep client_secret secure
 */
app.post('/api/oauth/token', apiRateLimiter, async (req, res) => {
  const { code, redirect_uri } = req.body;

  if (!code || !redirect_uri) {
    return res.status(400).json({ error: 'code and redirect_uri required' });
  }

  try {
    // Exchange code for token with PreSuite (server-side, with secret)
    const response = await axios.post('https://presuite.eu/api/oauth/token', {
      grant_type: 'authorization_code',
      code,
      redirect_uri,
      client_id: 'preoffice',
      client_secret: process.env.OAUTH_CLIENT_SECRET
    }, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      timeout: 10000
    });

    // Return tokens to frontend (without exposing client_secret)
    res.json({
      access_token: response.data.access_token,
      id_token: response.data.id_token,
      token_type: response.data.token_type,
      expires_in: response.data.expires_in
    });
  } catch (error) {
    logger.error('OAuth token exchange failed', { error: error.message });
    res.status(401).json({ error: 'Token exchange failed' });
  }
});

/**
 * Get editor URL for an existing file
 * POST /api/edit
 */
app.post('/api/edit', editRateLimiter, requireBearerAuth, async (req, res) => {
  const { filePath, nodeId } = req.body;
  const { userId, name: userName, token: userToken } = req.auth;

  if (!filePath && !nodeId) {
    return res.status(400).json({ error: 'filePath or nodeId required' });
  }

  try {
    let actualFilePath = filePath;
    let actualNodeId = nodeId;

    if (config.usePreDrive && nodeId && userToken) {
      try {
        const nodeResponse = await predriveRequest('GET', `/nodes/${nodeId}`, userToken);
        const node = nodeResponse.data;
        actualFilePath = node.name;
        logger.info('Editing PreDrive file', { nodeId });
      } catch (error) {
        logger.error('Failed to fetch file from PreDrive');
        if (!filePath) {
          return res.status(404).json({ error: 'File not found in PreDrive' });
        }
      }
    }

    const fileId = Buffer.from(actualFilePath || `/file-${nodeId}`).toString('base64');

    const accessToken = generateAccessToken(
      userId,
      fileId,
      actualNodeId,
      userToken,
      userName
    );

    const ext = (actualFilePath || '').split('.').pop().toLowerCase();
    const action = ['pdf'].includes(ext) ? 'view' : 'edit';

    const wopiSrc = encodeURIComponent(`${config.wopiBaseUrl}/files/${fileId}`);
    const collaboraEditorUrl = `${config.collaboraPublicUrl}/browser/dist/cool.html?WOPISrc=${wopiSrc}&access_token=${accessToken}`;

    res.json({
      editorUrl: collaboraEditorUrl,
      fileId,
      nodeId: actualNodeId,
      accessToken,
      expiresIn: config.tokenExpiry,
      mode: action
    });
  } catch (error) {
    logger.error('Edit endpoint error', { error: error.message });
    res.status(500).json({ error: 'Failed to generate editor URL' });
  }
});

/**
 * Create new document
 * POST /api/create
 */
app.post('/api/create', createRateLimiterMiddleware, requireBearerAuth, async (req, res) => {
  const { type, folder, parentId, name } = req.body;
  const { userId, name: userName, token: userToken } = req.auth;

  const templates = {
    document: { ext: 'odt', template: 'empty.odt' },
    spreadsheet: { ext: 'ods', template: 'empty.ods' },
    presentation: { ext: 'odp', template: 'empty.odp' },
    drawing: { ext: 'odg', template: 'empty.odg' }
  };

  const docType = templates[type] || templates.document;
  const rawFileName = name || `Untitled.${docType.ext}`;
  const fileName = sanitizeFilename(rawFileName) || `Untitled.${docType.ext}`;
  const filePath = `${folder || '/'}/${fileName}`.replace('//', '/');

  try {
    let nodeId = null;

    if (config.usePreDrive && userToken) {
      try {
        const startResponse = await predriveRequest('POST', '/nodes/files/upload/start', userToken, {
          parentId: parentId || null,
          fileName,
          mime: getMimeType(fileName),
          size: 0
        });

        const { sessionId, uploadUrl } = startResponse.data;

        if (uploadUrl) {
          await axios.put(uploadUrl, Buffer.alloc(0), {
            headers: {
              'Content-Type': 'application/octet-stream',
              'Content-Length': 0
            },
            timeout: 30000
          });
        }

        const completeResponse = await predriveRequest('POST', '/nodes/files/upload/complete', userToken, {
          sessionId
        });

        nodeId = completeResponse.data.nodeId;
        logger.info('Created new file in PreDrive', { fileName, nodeId });
      } catch (error) {
        logger.error('Failed to create file in PreDrive', { error: error.message });
      }
    }

    const fileId = Buffer.from(filePath).toString('base64');

    const accessToken = generateAccessToken(
      userId,
      fileId,
      nodeId,
      userToken,
      userName
    );

    const wopiSrc = encodeURIComponent(`${config.wopiBaseUrl}/files/${fileId}`);
    const collaboraEditorUrl = `${config.collaboraPublicUrl}/browser/dist/cool.html?WOPISrc=${wopiSrc}&access_token=${accessToken}`;

    res.json({
      filePath,
      fileName,
      nodeId,
      editorUrl: collaboraEditorUrl,
      fileId,
      accessToken,
      type: docType.ext
    });
  } catch (error) {
    logger.error('Create endpoint error', { error: error.message });
    res.status(500).json({ error: 'Failed to create document' });
  }
});

/**
 * List recent documents from PreDrive
 * GET /api/recent
 */
app.get('/api/recent', apiRateLimiter, requireBearerAuth, async (req, res) => {
  const { token: userToken } = req.auth;

  if (!config.usePreDrive) {
    return res.json({ files: [] });
  }

  try {
    const response = await predriveRequest('GET', '/nodes/recent', userToken);
    const files = response.data.filter(node => {
      const ext = (node.name || '').split('.').pop().toLowerCase();
      return ['odt', 'ods', 'odp', 'odg', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'pdf'].includes(ext);
    });

    res.json({
      files: files.map(node => ({
        nodeId: node.id,
        name: node.name,
        path: node.path || `/${node.name}`,
        type: getDocumentType(node.name),
        size: node.file?.size || 0,
        updatedAt: node.updatedAt,
        createdAt: node.createdAt
      }))
    });
  } catch (error) {
    logger.error('Recent files error', { error: error.message });
    res.json({ files: [] });
  }
});

/**
 * Health check
 */
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'PreOffice WOPI Server',
    version: '2.0.0',
    predriveEnabled: config.usePreDrive
  });
});

// =============================================================================
// Session Cleanup
// =============================================================================

setInterval(() => {
  const now = Date.now();
  let cleaned = 0;

  for (const [sessionId, data] of sessionStore.entries()) {
    if (now - data.createdAt > SESSION_EXPIRY_MS) {
      sessionStore.delete(sessionId);
      cleaned++;
    }
  }

  if (cleaned > 0 || sessionStore.size > 0) {
    logger.info('Session cleanup', { cleaned, active: sessionStore.size });
  }
}, SESSION_CLEANUP_INTERVAL_MS);

// =============================================================================
// Error Handler
// =============================================================================

app.use((err, req, res, next) => {
  logger.error('Unhandled error', { error: err.message, stack: IS_PRODUCTION ? undefined : err.stack });
  res.status(500).json({ error: 'Internal server error' });
});

// =============================================================================
// Start Server
// =============================================================================

app.listen(PORT, () => {
  logger.info('PreOffice WOPI Server started', {
    port: PORT,
    predriveEnabled: config.usePreDrive,
    production: IS_PRODUCTION
  });
});

module.exports = app;
