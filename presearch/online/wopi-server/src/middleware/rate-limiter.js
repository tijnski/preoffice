/**
 * Rate Limiting Middleware for PreOffice WOPI Server
 * Protects against abuse and DoS attacks
 */

const {
  API_RATE_LIMIT_WINDOW_MS,
  API_RATE_LIMIT_MAX,
  EDIT_RATE_LIMIT_MAX,
  CREATE_RATE_LIMIT_MAX,
  WOPI_RATE_LIMIT_MAX,
  RATE_LIMIT_CLEANUP_INTERVAL_MS
} = require('../config/constants');

// In-memory store for rate limiting (use Redis in production for distributed systems)
const rateLimitStore = new Map();

/**
 * Create a rate limiter middleware
 * @param {object} options - Rate limiter options
 * @param {number} options.windowMs - Time window in milliseconds
 * @param {number} options.max - Maximum requests per window
 * @param {string} options.keyPrefix - Prefix for the rate limit key
 * @param {function} options.keyGenerator - Function to generate the key (defaults to IP)
 */
function createRateLimiter({ windowMs = API_RATE_LIMIT_WINDOW_MS, max = API_RATE_LIMIT_MAX, keyPrefix = 'rl', keyGenerator }) {
  return (req, res, next) => {
    // Generate key for this request
    const ip = req.headers['x-forwarded-for']?.split(',')[0]?.trim() || req.ip || req.connection.remoteAddress || 'unknown';
    const key = keyGenerator ? `${keyPrefix}:${keyGenerator(req)}` : `${keyPrefix}:${ip}`;

    const now = Date.now();
    const record = rateLimitStore.get(key);

    if (!record || now - record.startTime > windowMs) {
      // New window
      rateLimitStore.set(key, {
        count: 1,
        startTime: now
      });
      setRateLimitHeaders(res, max, max - 1, windowMs);
      return next();
    }

    // Increment counter
    record.count++;

    if (record.count > max) {
      const retryAfter = Math.ceil((record.startTime + windowMs - now) / 1000);
      setRateLimitHeaders(res, max, 0, windowMs, retryAfter);

      return res.status(429).json({
        error: 'Too Many Requests',
        message: `Rate limit exceeded. Try again in ${retryAfter} seconds.`,
        retryAfter
      });
    }

    setRateLimitHeaders(res, max, max - record.count, windowMs);
    next();
  };
}

/**
 * Set rate limit headers on response
 */
function setRateLimitHeaders(res, limit, remaining, windowMs, retryAfter) {
  res.set('X-RateLimit-Limit', limit);
  res.set('X-RateLimit-Remaining', Math.max(0, remaining));
  res.set('X-RateLimit-Reset', Math.ceil((Date.now() + windowMs) / 1000));
  if (retryAfter) {
    res.set('Retry-After', retryAfter);
  }
}

// Clean up expired entries periodically
setInterval(() => {
  const now = Date.now();
  let cleaned = 0;

  for (const [key, record] of rateLimitStore.entries()) {
    if (now - record.startTime > API_RATE_LIMIT_WINDOW_MS * 2) {
      rateLimitStore.delete(key);
      cleaned++;
    }
  }

  if (cleaned > 0) {
    console.log(`[RateLimiter] Cleaned ${cleaned} expired entries, ${rateLimitStore.size} active`);
  }
}, RATE_LIMIT_CLEANUP_INTERVAL_MS);

// Pre-configured rate limiters
const apiRateLimiter = createRateLimiter({
  windowMs: API_RATE_LIMIT_WINDOW_MS,
  max: API_RATE_LIMIT_MAX,
  keyPrefix: 'api'
});

const editRateLimiter = createRateLimiter({
  windowMs: API_RATE_LIMIT_WINDOW_MS,
  max: EDIT_RATE_LIMIT_MAX,
  keyPrefix: 'edit'
});

const createRateLimiterMiddleware = createRateLimiter({
  windowMs: API_RATE_LIMIT_WINDOW_MS,
  max: CREATE_RATE_LIMIT_MAX,
  keyPrefix: 'create'
});

const wopiRateLimiter = createRateLimiter({
  windowMs: API_RATE_LIMIT_WINDOW_MS,
  max: WOPI_RATE_LIMIT_MAX,
  keyPrefix: 'wopi'
});

module.exports = {
  createRateLimiter,
  apiRateLimiter,
  editRateLimiter,
  createRateLimiterMiddleware,
  wopiRateLimiter
};
