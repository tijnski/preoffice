/**
 * Secure Logger for PreOffice WOPI Server
 * Masks sensitive data to prevent information leakage
 */

const { IS_PRODUCTION, LOG_LEVEL, SENSITIVE_FIELDS } = require('../config/constants');

/**
 * Mask sensitive values in log data
 */
function maskSensitiveData(data) {
  if (!data) return data;

  if (typeof data === 'string') {
    // Mask JWT tokens
    if (data.match(/^eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]*$/)) {
      return 'eyJ***[REDACTED]***';
    }
    // Mask email addresses
    if (data.includes('@')) {
      return data.replace(/([a-zA-Z0-9])[a-zA-Z0-9.]*(@[a-zA-Z0-9.-]+)/, '$1***$2');
    }
    // Mask UUIDs
    if (data.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i)) {
      return data.substring(0, 8) + '-****-****-****-************';
    }
    return data;
  }

  if (Array.isArray(data)) {
    return data.map(maskSensitiveData);
  }

  if (typeof data === 'object') {
    const masked = {};
    for (const [key, value] of Object.entries(data)) {
      const lowerKey = key.toLowerCase();
      if (SENSITIVE_FIELDS.some(field => lowerKey.includes(field))) {
        masked[key] = '[REDACTED]';
      } else {
        masked[key] = maskSensitiveData(value);
      }
    }
    return masked;
  }

  return data;
}

/**
 * Format log message
 */
function formatLog(level, message, data) {
  const timestamp = new Date().toISOString();
  const maskedData = maskSensitiveData(data);

  if (IS_PRODUCTION) {
    // Structured JSON logging in production
    return JSON.stringify({
      timestamp,
      level,
      service: 'preoffice-wopi',
      message,
      ...(maskedData && { data: maskedData })
    });
  }

  // Human-readable in development
  let log = `[${timestamp}] [${level.toUpperCase()}] ${message}`;
  if (maskedData) {
    log += ` ${JSON.stringify(maskedData)}`;
  }
  return log;
}

/**
 * Log levels hierarchy
 */
const LOG_LEVELS = {
  error: 0,
  warn: 1,
  info: 2,
  debug: 3
};

/**
 * Check if log level should be output
 */
function shouldLog(level) {
  const configuredLevel = LOG_LEVELS[LOG_LEVEL] ?? LOG_LEVELS.info;
  const requestedLevel = LOG_LEVELS[level] ?? LOG_LEVELS.info;
  return requestedLevel <= configuredLevel;
}

/**
 * Secure logger instance
 */
const logger = {
  error(message, data) {
    if (shouldLog('error')) {
      console.error(formatLog('error', message, data));
    }
  },

  warn(message, data) {
    if (shouldLog('warn')) {
      console.warn(formatLog('warn', message, data));
    }
  },

  info(message, data) {
    if (shouldLog('info')) {
      console.log(formatLog('info', message, data));
    }
  },

  debug(message, data) {
    if (shouldLog('debug')) {
      console.log(formatLog('debug', message, data));
    }
  }
};

module.exports = { logger, maskSensitiveData };
