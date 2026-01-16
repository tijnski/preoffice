/**
 * Authentication Middleware for PreOffice WOPI Server
 * Handles JWT verification and PreSuite token validation
 */

const jwt = require('jsonwebtoken');
const axios = require('axios');
const { JWT_SECRET, JWT_ISSUER, IS_PRODUCTION } = require('../config/constants');
const { logger } = require('../utils/logger');

/**
 * Verify PreSuite JWT token by calling the auth API
 * This validates that the token was actually issued by PreSuite
 */
async function verifyPresuitToken(token) {
  try {
    const response = await axios.get('https://presuite.eu/api/auth/verify', {
      headers: {
        'Authorization': `Bearer ${token}`
      },
      timeout: 5000
    });

    return response.data.valid ? response.data.user : null;
  } catch (error) {
    logger.warn('PreSuite token verification failed', { error: error.message });
    return null;
  }
}

/**
 * Middleware to require authentication via PreSuite Bearer token
 * Used for /api/* endpoints
 */
async function requireBearerAuth(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Authorization header required'
    });
  }

  const token = authHeader.slice(7);

  if (!token) {
    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Token required'
    });
  }

  try {
    // First try to verify with PreSuite
    const user = await verifyPresuitToken(token);

    if (user) {
      req.auth = {
        userId: user.id || user.sub,
        email: user.email,
        name: user.name,
        orgId: user.org_id || user.orgId,
        token: token
      };
      return next();
    }

    // If PreSuite verification fails, try local JWT verification (for WOPI tokens)
    try {
      const decoded = jwt.verify(token, JWT_SECRET, {
        issuer: JWT_ISSUER
      });

      req.auth = {
        userId: decoded.userId || decoded.sub,
        email: decoded.email,
        name: decoded.name,
        sessionId: decoded.sessionId,
        token: token
      };
      return next();
    } catch (jwtError) {
      // Both verifications failed
      logger.warn('Authentication failed', {
        presuiteError: 'Token not valid',
        jwtError: jwtError.message
      });
    }

    return res.status(401).json({
      error: 'Unauthorized',
      message: 'Invalid or expired token'
    });
  } catch (error) {
    logger.error('Authentication error', { error: error.message });
    return res.status(500).json({
      error: 'Authentication Error',
      message: 'Failed to verify authentication'
    });
  }
}

/**
 * Middleware to require WOPI access token
 * Used for /wopi/* endpoints
 */
function requireWopiAuth(sessionStore) {
  return (req, res, next) => {
    const token = req.query.access_token || req.headers['x-wopi-access-token'];

    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    try {
      const decoded = jwt.verify(token, JWT_SECRET);
      const session = sessionStore.get(decoded.sessionId);

      if (!session) {
        return res.status(401).json({ error: 'Session expired or invalid' });
      }

      req.auth = { ...decoded, session };
      next();
    } catch (err) {
      logger.warn('WOPI auth failed', { error: err.message });
      return res.status(401).json({ error: 'Invalid or expired token' });
    }
  };
}

/**
 * Optional authentication - sets req.auth if valid token present, but doesn't require it
 */
async function optionalAuth(req, res, next) {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return next();
  }

  const token = authHeader.slice(7);

  if (!token) {
    return next();
  }

  try {
    const user = await verifyPresuitToken(token);
    if (user) {
      req.auth = {
        userId: user.id || user.sub,
        email: user.email,
        name: user.name,
        orgId: user.org_id || user.orgId,
        token: token
      };
    }
  } catch (error) {
    // Ignore errors for optional auth
  }

  next();
}

module.exports = {
  verifyPresuitToken,
  requireBearerAuth,
  requireWopiAuth,
  optionalAuth
};
