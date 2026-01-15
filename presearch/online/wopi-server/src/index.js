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

// Persistent storage directory (fallback for demo mode)
const STORAGE_DIR = process.env.STORAGE_DIR || '/data/preoffice-files';

// Ensure storage directory exists
if (!fs.existsSync(STORAGE_DIR)) {
  fs.mkdirSync(STORAGE_DIR, { recursive: true });
  console.log(`Created storage directory: ${STORAGE_DIR}`);
}

const app = express();
const PORT = process.env.PORT || 8080;

// Configuration
const config = {
  predriveApiUrl: process.env.PREDRIVE_API_URL || 'https://predrive.eu/api',
  wopiBaseUrl: process.env.WOPI_BASE_URL || 'http://host.docker.internal:8080/wopi',
  collaboraUrl: process.env.COLLABORA_URL || 'http://collabora:9980',
  collaboraPublicUrl: process.env.COLLABORA_PUBLIC_URL || 'http://localhost:8000',
  jwtSecret: process.env.JWT_SECRET || 'change-this-secret-in-production',
  tokenExpiry: '24h',
  // Enable PreDrive integration (set to false for demo mode)
  usePreDrive: process.env.USE_PREDRIVE === 'true'
};

// Middleware
app.use(helmet({ contentSecurityPolicy: false }));
app.use(cors());
app.use(morgan('combined'));
app.use(express.json());
app.use(express.raw({ type: 'application/octet-stream', limit: '100mb' }));

// In-memory stores (use Redis in production for distributed systems)
const fileLocks = new Map();
const sessionStore = new Map(); // Store user tokens and file metadata by session

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
 * Verify access token and get session data
 */
function verifyAccessToken(token) {
  try {
    const decoded = jwt.verify(token, config.jwtSecret);
    const session = sessionStore.get(decoded.sessionId);
    return { ...decoded, session };
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
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });
    return response;
  } catch (error) {
    console.error(`PreDrive API error [${method} ${endpoint}]:`, error.response?.data || error.message);
    throw error;
  }
}

/**
 * Download file content from PreDrive
 */
async function downloadFromPreDrive(nodeId, userToken) {
  try {
    // Get download URL from PreDrive
    const response = await predriveRequest('GET', `/nodes/files/${nodeId}/download`, userToken);
    const downloadUrl = response.data.downloadUrl;

    if (!downloadUrl) {
      throw new Error('No download URL returned from PreDrive');
    }

    // Download the file content
    const fileResponse = await axios.get(downloadUrl, {
      responseType: 'arraybuffer',
      maxContentLength: Infinity
    });

    return Buffer.from(fileResponse.data);
  } catch (error) {
    console.error('Failed to download from PreDrive:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Upload file content to PreDrive
 * Uses the direct content update endpoint for existing files
 */
async function uploadToPreDrive(nodeId, content, fileName, userToken) {
  try {
    const mime = getMimeType(fileName);

    // Use the direct content update endpoint (creates new version)
    const response = await axios.put(
      `${config.predriveApiUrl}/nodes/files/${nodeId}/content`,
      content,
      {
        headers: {
          'Authorization': `Bearer ${userToken}`,
          'Content-Type': mime,
          'Content-Length': content.length
        },
        maxContentLength: Infinity,
        maxBodyLength: Infinity
      }
    );

    return response.data;
  } catch (error) {
    console.error('Failed to upload to PreDrive:', error.response?.data || error.message);
    throw error;
  }
}

/**
 * Get MIME type from filename
 */
function getMimeType(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  const mimeTypes = {
    // Documents
    odt: 'application/vnd.oasis.opendocument.text',
    doc: 'application/msword',
    docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    rtf: 'application/rtf',
    txt: 'text/plain',
    // Spreadsheets
    ods: 'application/vnd.oasis.opendocument.spreadsheet',
    xls: 'application/vnd.ms-excel',
    xlsx: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    csv: 'text/csv',
    // Presentations
    odp: 'application/vnd.oasis.opendocument.presentation',
    ppt: 'application/vnd.ms-powerpoint',
    pptx: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    // Drawings
    odg: 'application/vnd.oasis.opendocument.graphics',
    // Other
    pdf: 'application/pdf'
  };
  return mimeTypes[ext] || 'application/octet-stream';
}

/**
 * Get file extension and determine document type
 */
function getDocumentType(filename) {
  const ext = filename.split('.').pop().toLowerCase();
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

// Legacy in-memory fallback
const demoFiles = new Map();

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

/**
 * CheckFileInfo - Get file metadata
 * GET /wopi/files/{fileId}
 */
app.get('/wopi/files/:fileId', requireAuth, async (req, res) => {
  const { fileId } = req.params;
  const { userId, nodeId, session } = req.auth;

  try {
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    const fileName = filePath.split('/').pop();
    console.log(`CheckFileInfo for: ${filePath} (nodeId: ${nodeId})`);

    let fileSize = 0;
    let lastModified = new Date();
    let userName = session?.userName || 'User';
    let version = Date.now().toString();

    // Try to get file info from PreDrive
    if (config.usePreDrive && nodeId && session?.userToken) {
      try {
        const nodeResponse = await predriveRequest('GET', `/nodes/${nodeId}`, session.userToken);
        const node = nodeResponse.data;
        fileSize = node.file?.size || 0;
        lastModified = new Date(node.updatedAt || node.createdAt);
        version = node.file?.currentVersion?.toString() || version;
      } catch (error) {
        console.log('PreDrive lookup failed, using defaults:', error.message);
      }
    } else {
      // Demo mode: check local storage
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
      UserFriendlyName: userName,
      IsAnonymousUser: false,

      // Branding
      BreadcrumbBrandName: 'PreOffice',
      BreadcrumbBrandUrl: config.collaboraPublicUrl,
      BreadcrumbFolderName: filePath.split('/').slice(0, -1).join('/') || '/',
      BreadcrumbFolderUrl: config.collaboraPublicUrl,

      // Features
      DisablePrint: false,
      DisableExport: false,
      DisableCopy: false,
      EnableOwnerTermination: true,

      // PostMessage
      PostMessageOrigin: config.collaboraPublicUrl,

      // Last modified
      LastModifiedTime: lastModified.toISOString()
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
  const { nodeId, session } = req.auth;

  try {
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    console.log(`GetFile for: ${filePath} (nodeId: ${nodeId})`);

    // Try PreDrive first
    if (config.usePreDrive && nodeId && session?.userToken) {
      try {
        const content = await downloadFromPreDrive(nodeId, session.userToken);
        console.log(`Returning PreDrive file content (${content.length} bytes)`);
        res.set('Content-Type', 'application/octet-stream');
        return res.send(content);
      } catch (error) {
        console.log('PreDrive download failed, trying local storage:', error.message);
      }
    }

    // Try persistent storage
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
  const { nodeId, session } = req.auth;
  const lockId = req.headers['x-wopi-lock'];

  try {
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    const fileName = filePath.split('/').pop();
    console.log(`PutFile for: ${filePath} (nodeId: ${nodeId})`);

    // Check lock
    const currentLock = fileLocks.get(fileId);
    if (currentLock && currentLock !== lockId) {
      res.set('X-WOPI-Lock', currentLock);
      return res.status(409).json({ error: 'File is locked' });
    }

    const content = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body);
    let newVersion = Date.now().toString();

    // Try to save to PreDrive
    if (config.usePreDrive && nodeId && session?.userToken) {
      try {
        const result = await uploadToPreDrive(nodeId, content, fileName, session.userToken);
        newVersion = result.version?.toString() || newVersion;
        console.log(`Saved to PreDrive (${content.length} bytes, version: ${newVersion})`);
      } catch (error) {
        console.log('PreDrive upload failed, saving to local storage:', error.message);
        // Fall back to local storage
        writeFileToStorage(fileId, content);
        demoFiles.set(fileId, content);
      }
    } else {
      // Demo mode: save to local storage
      writeFileToStorage(fileId, content);
      demoFiles.set(fileId, content);
    }

    res.json({
      ItemVersion: newVersion
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
  const { nodeId, session } = req.auth;
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
      // Create new file relative to current file
      return handlePutRelative(req, res, fileId, session);

    case 'RENAME_FILE':
      return handleRenameFile(req, res, fileId, nodeId, session);

    case 'DELETE':
      return handleDeleteFile(req, res, fileId, nodeId, lockId, currentLock, session);

    default:
      return res.status(400).json({ error: 'Unknown operation' });
  }
});

/**
 * Handle PUT_RELATIVE - Create new file with suggested name
 */
async function handlePutRelative(req, res, fileId, session) {
  const suggestedName = req.headers['x-wopi-suggestedtarget'];
  const relativeName = req.headers['x-wopi-relativetarget'];
  const overwrite = req.headers['x-wopi-overwriterelativetarget'] === 'true';

  if (!config.usePreDrive || !session?.userToken) {
    return res.status(501).json({ error: 'PreDrive integration not configured' });
  }

  try {
    const filePath = Buffer.from(fileId, 'base64').toString('utf8');
    const folderPath = filePath.split('/').slice(0, -1).join('/') || '/';

    // Determine new filename
    let newFileName = relativeName || suggestedName;
    if (newFileName.startsWith('.')) {
      // Extension only - replace current extension
      const baseName = filePath.split('/').pop().split('.').slice(0, -1).join('.');
      newFileName = baseName + newFileName;
    }

    const newFilePath = `${folderPath}/${newFileName}`.replace('//', '/');
    const newFileId = Buffer.from(newFilePath).toString('base64');

    // Create empty file in PreDrive
    const content = Buffer.isBuffer(req.body) ? req.body : Buffer.from(req.body || '');

    // Store content locally for now (full implementation would upload to PreDrive)
    writeFileToStorage(newFileId, content);
    demoFiles.set(newFileId, content);

    // Generate new access token for the new file
    const newAccessToken = generateAccessToken(
      session.userId,
      newFileId,
      null, // New file doesn't have PreDrive node ID yet
      session.userToken,
      session.userName
    );

    res.json({
      Name: newFileName,
      Url: `${config.wopiBaseUrl}/files/${newFileId}?access_token=${newAccessToken}`
    });
  } catch (error) {
    console.error('PUT_RELATIVE error:', error.message);
    res.status(500).json({ error: 'Failed to create file' });
  }
}

/**
 * Handle RENAME_FILE - Rename file in PreDrive
 */
async function handleRenameFile(req, res, fileId, nodeId, session) {
  const newName = req.headers['x-wopi-requestedname'];

  if (!newName) {
    return res.status(400).json({ error: 'New name required' });
  }

  if (!config.usePreDrive || !nodeId || !session?.userToken) {
    // Demo mode - just return success with new name
    return res.json({ Name: newName });
  }

  try {
    await predriveRequest('PATCH', `/nodes/${nodeId}`, session.userToken, {
      name: newName
    });

    res.json({ Name: newName });
  } catch (error) {
    console.error('RENAME_FILE error:', error.message);
    res.status(500).json({ error: 'Failed to rename file' });
  }
}

/**
 * Handle DELETE - Delete file from PreDrive
 */
async function handleDeleteFile(req, res, fileId, nodeId, lockId, currentLock, session) {
  if (currentLock && currentLock !== lockId) {
    res.set('X-WOPI-Lock', currentLock);
    return res.status(409).json({ error: 'File is locked' });
  }

  if (!config.usePreDrive || !nodeId || !session?.userToken) {
    // Demo mode - delete from local storage
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
    console.error('DELETE error:', error.message);
    res.status(500).json({ error: 'Failed to delete file' });
  }
}

// =============================================================================
// PreOffice Online Frontend Endpoints
// =============================================================================

/**
 * Get editor URL for an existing file
 * POST /api/edit
 */
app.post('/api/edit', async (req, res) => {
  const { filePath, nodeId, userToken, userId, userName } = req.body;

  if (!userToken) {
    return res.status(400).json({ error: 'userToken required' });
  }

  if (!filePath && !nodeId) {
    return res.status(400).json({ error: 'filePath or nodeId required' });
  }

  try {
    let actualFilePath = filePath;
    let actualNodeId = nodeId;
    let fileSize = 0;

    // If we have a nodeId, fetch file info from PreDrive
    if (config.usePreDrive && nodeId && userToken) {
      try {
        const nodeResponse = await predriveRequest('GET', `/nodes/${nodeId}`, userToken);
        const node = nodeResponse.data;
        actualFilePath = node.name; // Use node name as the file path
        fileSize = node.file?.size || 0;
        console.log(`Editing PreDrive file: ${node.name} (nodeId: ${nodeId}, size: ${fileSize})`);
      } catch (error) {
        console.error('Failed to fetch file from PreDrive:', error.message);
        if (!filePath) {
          return res.status(404).json({ error: 'File not found in PreDrive' });
        }
      }
    }

    // Generate file ID (base64 encoded path)
    const fileId = Buffer.from(actualFilePath || `/file-${nodeId}`).toString('base64');

    // Generate WOPI access token with session data
    const accessToken = generateAccessToken(
      userId || 'anonymous',
      fileId,
      actualNodeId,
      userToken,
      userName
    );

    // Get file extension to determine editor action
    const ext = (actualFilePath || '').split('.').pop().toLowerCase();
    const action = ['pdf'].includes(ext) ? 'view' : 'edit';

    // Build Collabora URL
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
    console.error('Edit endpoint error:', error.message);
    res.status(500).json({ error: 'Failed to generate editor URL' });
  }
});

/**
 * Create new document
 * POST /api/create
 */
app.post('/api/create', async (req, res) => {
  const { type, folder, parentId, name, userToken, userId, userName } = req.body;

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
    let nodeId = null;

    // Create file in PreDrive if enabled
    if (config.usePreDrive && userToken) {
      try {
        // Create empty file in PreDrive
        // First, start an upload session
        const startResponse = await predriveRequest('POST', '/nodes/files/upload/start', userToken, {
          parentId: parentId || null,
          fileName,
          mime: getMimeType(fileName),
          size: 0
        });

        const { sessionId, uploadUrl } = startResponse.data;

        // For empty documents, we can complete immediately
        // Collabora will populate the content when user saves
        if (uploadUrl) {
          // Upload empty content
          await axios.put(uploadUrl, Buffer.alloc(0), {
            headers: {
              'Content-Type': 'application/octet-stream',
              'Content-Length': 0
            }
          });
        }

        // Complete upload
        const completeResponse = await predriveRequest('POST', '/nodes/files/upload/complete', userToken, {
          sessionId
        });

        nodeId = completeResponse.data.nodeId;
        console.log(`Created new file in PreDrive: ${fileName} (nodeId: ${nodeId})`);
      } catch (error) {
        console.error('Failed to create file in PreDrive:', error.message);
        // Continue with demo mode
      }
    }

    // Generate file ID
    const fileId = Buffer.from(filePath).toString('base64');

    // Generate access token
    const accessToken = generateAccessToken(
      userId || 'anonymous',
      fileId,
      nodeId,
      userToken,
      userName
    );

    // Build Collabora URL
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
    console.error('Create endpoint error:', error.message);
    res.status(500).json({ error: 'Failed to create document' });
  }
});

/**
 * List recent documents from PreDrive
 * GET /api/recent
 */
app.get('/api/recent', async (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Authorization required' });
  }

  const userToken = authHeader.slice(7);

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
    console.error('Recent files error:', error.message);
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
    version: '1.1.0',
    collabora: config.collaboraPublicUrl,
    predrive: config.predriveApiUrl,
    predriveEnabled: config.usePreDrive
  });
});

// =============================================================================
// Session Cleanup
// =============================================================================

// Clean up expired sessions every hour
setInterval(() => {
  const now = Date.now();
  const maxAge = 24 * 60 * 60 * 1000; // 24 hours

  for (const [sessionId, data] of sessionStore.entries()) {
    if (now - data.createdAt > maxAge) {
      sessionStore.delete(sessionId);
    }
  }

  console.log(`Session cleanup: ${sessionStore.size} active sessions`);
}, 60 * 60 * 1000);

// =============================================================================
// Start Server
// =============================================================================

app.listen(PORT, () => {
  console.log(`
╔═══════════════════════════════════════════════════════════╗
║           PreOffice Online - WOPI Server v1.1             ║
╠═══════════════════════════════════════════════════════════╣
║  Port:           ${PORT}                                       ║
║  PreDrive:       ${config.predriveApiUrl.padEnd(33)}   ║
║  PreDrive Mode:  ${(config.usePreDrive ? 'ENABLED' : 'DISABLED (Demo)').padEnd(33)}   ║
║  Collabora:      ${config.collaboraUrl.padEnd(33)}   ║
╚═══════════════════════════════════════════════════════════╝
  `);
});

module.exports = app;
