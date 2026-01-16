/**
 * Security Middleware for PreOffice WOPI Server
 * Implements various security measures
 */

const { IS_PRODUCTION, CSP_DIRECTIVES, CORS_ALLOWED_ORIGINS } = require('../config/constants');

/**
 * Security headers middleware
 * Sets various security headers to protect against common attacks
 */
function securityHeaders(req, res, next) {
  // Prevent clickjacking
  res.set('X-Frame-Options', 'SAMEORIGIN');

  // Prevent MIME type sniffing
  res.set('X-Content-Type-Options', 'nosniff');

  // XSS protection (legacy, but still useful for older browsers)
  res.set('X-XSS-Protection', '1; mode=block');

  // Referrer policy
  res.set('Referrer-Policy', 'strict-origin-when-cross-origin');

  // Permissions policy (disable features we don't need)
  res.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=(), interest-cohort=()');

  // HSTS in production
  if (IS_PRODUCTION) {
    res.set('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  }

  // Cache control for API responses
  if (req.path.startsWith('/api/') || req.path.startsWith('/wopi/')) {
    res.set('Cache-Control', 'no-store, no-cache, must-revalidate, private');
    res.set('Pragma', 'no-cache');
    res.set('Expires', '0');
  }

  next();
}

/**
 * Content Security Policy middleware
 * Configured to allow Collabora Online to function
 */
function contentSecurityPolicy(req, res, next) {
  // Build CSP header
  const directives = Object.entries(CSP_DIRECTIVES)
    .map(([key, values]) => {
      const directiveName = key.replace(/([A-Z])/g, '-$1').toLowerCase();
      return `${directiveName} ${values.join(' ')}`;
    })
    .join('; ');

  res.set('Content-Security-Policy', directives);
  next();
}

/**
 * CORS middleware with origin validation
 */
function corsMiddleware(req, res, next) {
  const origin = req.headers.origin;

  // Check if origin is allowed
  if (origin && CORS_ALLOWED_ORIGINS.includes(origin)) {
    res.set('Access-Control-Allow-Origin', origin);
    res.set('Access-Control-Allow-Credentials', 'true');
  } else if (!IS_PRODUCTION && origin) {
    // In development, allow localhost origins
    if (origin.includes('localhost') || origin.includes('127.0.0.1')) {
      res.set('Access-Control-Allow-Origin', origin);
      res.set('Access-Control-Allow-Credentials', 'true');
    }
  }

  // Handle preflight
  if (req.method === 'OPTIONS') {
    res.set('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    res.set('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-WOPI-Override, X-WOPI-Lock, X-WOPI-OldLock, X-Share-Password');
    res.set('Access-Control-Max-Age', '86400');
    return res.status(204).end();
  }

  next();
}

/**
 * Validate and sanitize file ID (base64 encoded path)
 * Prevents path traversal and injection attacks
 */
function validateFileId(fileId) {
  if (!fileId || typeof fileId !== 'string') {
    return { valid: false, error: 'File ID is required' };
  }

  // Check for reasonable length
  if (fileId.length > 1000) {
    return { valid: false, error: 'File ID too long' };
  }

  // Validate base64 format
  const base64Pattern = /^[A-Za-z0-9+/=_-]+$/;
  if (!base64Pattern.test(fileId)) {
    return { valid: false, error: 'Invalid file ID format' };
  }

  try {
    // Decode and validate the path
    const decoded = Buffer.from(fileId, 'base64').toString('utf8');

    // Check for path traversal attempts
    if (decoded.includes('..') || decoded.includes('\0')) {
      return { valid: false, error: 'Invalid path' };
    }

    // Check for absolute paths outside allowed directories
    if (decoded.startsWith('/etc/') || decoded.startsWith('/root/') ||
        decoded.startsWith('/var/') || decoded.includes('/./')) {
      return { valid: false, error: 'Invalid path' };
    }

    return { valid: true, path: decoded };
  } catch (err) {
    return { valid: false, error: 'Invalid file ID encoding' };
  }
}

/**
 * Sanitize filename to prevent path traversal and injection
 */
function sanitizeFilename(filename) {
  if (!filename || typeof filename !== 'string') {
    return null;
  }

  // Remove path components
  let safe = filename.split('/').pop().split('\\').pop();

  // Remove null bytes and control characters
  safe = safe.replace(/[\x00-\x1f\x7f]/g, '');

  // Remove leading/trailing dots and spaces
  safe = safe.replace(/^[.\s]+|[.\s]+$/g, '');

  // Replace dangerous characters
  safe = safe.replace(/[<>:"|?*]/g, '_');

  // Limit length
  if (safe.length > 255) {
    const ext = safe.split('.').pop();
    const base = safe.substring(0, 240);
    safe = `${base}.${ext}`;
  }

  return safe || null;
}

module.exports = {
  securityHeaders,
  contentSecurityPolicy,
  corsMiddleware,
  validateFileId,
  sanitizeFilename
};
