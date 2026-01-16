/**
 * PreOffice WOPI Server Constants
 * Centralized configuration values to avoid magic numbers throughout the codebase
 */

// =============================================================================
// ENVIRONMENT VALIDATION
// =============================================================================

const IS_PRODUCTION = process.env.NODE_ENV === 'production';

/**
 * Get a required environment variable, throwing in production if not set
 */
function getRequiredEnv(name, defaultValue) {
  const value = process.env[name] || defaultValue;
  if (!value && IS_PRODUCTION) {
    throw new Error(`[Security] Required environment variable ${name} is not set in production`);
  }
  if (!value) {
    console.warn(`[Security] ${name} not set - using default value (not safe for production)`);
  }
  return value || '';
}

// =============================================================================
// SECURITY SECRETS (validated at startup in production)
// =============================================================================

/** JWT secret for token signing - MUST be set in production */
const JWT_SECRET = getRequiredEnv('JWT_SECRET', 'preoffice-dev-secret-DO-NOT-USE-IN-PRODUCTION');

/** OAuth client secret for PreSuite integration - MUST be set in production */
const OAUTH_CLIENT_SECRET = getRequiredEnv('OAUTH_CLIENT_SECRET', 'preoffice-dev-oauth-secret');

/** Collabora admin password */
const COLLABORA_ADMIN_PASS = getRequiredEnv('COLLABORA_ADMIN_PASS', 'change-this-password');

// =============================================================================
// JWT CONFIGURATION
// =============================================================================

/** JWT token expiry (reduced from 24h) */
const JWT_TOKEN_EXPIRY = '4h';

/** JWT algorithm */
const JWT_ALGORITHM = 'HS256';

/** JWT issuer */
const JWT_ISSUER = 'preoffice';

// =============================================================================
// RATE LIMITING
// =============================================================================

/** API rate limit window (1 minute) */
const API_RATE_LIMIT_WINDOW_MS = 60 * 1000;

/** Max API requests per window */
const API_RATE_LIMIT_MAX = 60;

/** Edit endpoint rate limit (per minute) */
const EDIT_RATE_LIMIT_MAX = 30;

/** Create endpoint rate limit (per minute) */
const CREATE_RATE_LIMIT_MAX = 20;

/** WOPI operations rate limit (per minute) */
const WOPI_RATE_LIMIT_MAX = 100;

/** Rate limiter cleanup interval */
const RATE_LIMIT_CLEANUP_INTERVAL_MS = 60 * 1000;

// =============================================================================
// FILE OPERATIONS
// =============================================================================

/** Maximum file upload size (100MB) */
const MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024;

/** Maximum filename length */
const MAX_FILENAME_LENGTH = 255;

/** Allowed filename pattern (safe characters only) */
const SAFE_FILENAME_PATTERN = /^[a-zA-Z0-9._\-\s()\[\]]+$/;

/** Allowed file extensions for editing */
const ALLOWED_EXTENSIONS = [
  'odt', 'ods', 'odp', 'odg',
  'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
  'rtf', 'txt', 'csv', 'pdf'
];

// =============================================================================
// SESSION MANAGEMENT
// =============================================================================

/** Session expiry (4 hours to match JWT) */
const SESSION_EXPIRY_MS = 4 * 60 * 60 * 1000;

/** Session cleanup interval (30 minutes) */
const SESSION_CLEANUP_INTERVAL_MS = 30 * 60 * 1000;

/** Maximum concurrent sessions per user */
const MAX_SESSIONS_PER_USER = 10;

// =============================================================================
// CORS CONFIGURATION
// =============================================================================

/** Allowed CORS origins (set via environment in production) */
const CORS_ALLOWED_ORIGINS = process.env.CORS_ORIGINS
  ? process.env.CORS_ORIGINS.split(',')
  : ['https://preoffice.site', 'https://predrive.eu', 'https://presuite.eu'];

// =============================================================================
// CONTENT SECURITY POLICY
// =============================================================================

/** CSP directives */
const CSP_DIRECTIVES = {
  defaultSrc: ["'self'"],
  scriptSrc: ["'self'", "'unsafe-inline'"], // Required for Collabora
  styleSrc: ["'self'", "'unsafe-inline'"],
  imgSrc: ["'self'", 'data:', 'blob:'],
  connectSrc: ["'self'", 'https://predrive.eu', 'https://presuite.eu'],
  frameSrc: ["'self'"],
  frameAncestors: ["'self'", 'https://predrive.eu'],
  formAction: ["'self'"],
  baseUri: ["'self'"]
};

// =============================================================================
// LOGGING
// =============================================================================

/** Log level */
const LOG_LEVEL = process.env.LOG_LEVEL || (IS_PRODUCTION ? 'warn' : 'info');

/** Sensitive fields to mask in logs */
const SENSITIVE_FIELDS = ['password', 'token', 'secret', 'authorization', 'cookie'];

module.exports = {
  IS_PRODUCTION,
  getRequiredEnv,
  // Secrets
  JWT_SECRET,
  OAUTH_CLIENT_SECRET,
  COLLABORA_ADMIN_PASS,
  // JWT
  JWT_TOKEN_EXPIRY,
  JWT_ALGORITHM,
  JWT_ISSUER,
  // Rate limiting
  API_RATE_LIMIT_WINDOW_MS,
  API_RATE_LIMIT_MAX,
  EDIT_RATE_LIMIT_MAX,
  CREATE_RATE_LIMIT_MAX,
  WOPI_RATE_LIMIT_MAX,
  RATE_LIMIT_CLEANUP_INTERVAL_MS,
  // Files
  MAX_FILE_SIZE_BYTES,
  MAX_FILENAME_LENGTH,
  SAFE_FILENAME_PATTERN,
  ALLOWED_EXTENSIONS,
  // Sessions
  SESSION_EXPIRY_MS,
  SESSION_CLEANUP_INTERVAL_MS,
  MAX_SESSIONS_PER_USER,
  // CORS
  CORS_ALLOWED_ORIGINS,
  // CSP
  CSP_DIRECTIVES,
  // Logging
  LOG_LEVEL,
  SENSITIVE_FIELDS
};
