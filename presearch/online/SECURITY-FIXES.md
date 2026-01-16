# PreOffice Security Fixes

> **Date:** January 16, 2026
> **Status:** Complete (All severity levels fixed)

---

## Summary

Security audit and fixes for the PreOffice Online WOPI server application.

| Severity | Issues Found | Fixed | Status |
|----------|--------------|-------|--------|
| Critical | 3 | 3 | Complete |
| High | 8 | 8 | Complete |
| Medium | 6 | 6 | Complete |
| Low | 4 | 4 | Complete |

---

## Critical Security Fixes

### 1. Hardcoded OAuth Client Secret in Frontend
**File:** `branding/static/index.html`
**Issue:** OAuth client secret was exposed in browser JavaScript
**Fix:** Moved token exchange to server-side endpoint `/api/oauth/token`

```javascript
// Before (INSECURE - secret in browser):
const OAUTH_CLIENT_SECRET = 'preoffice_secret_2026';
fetch(PRESUITE_TOKEN_URL, {
  body: { client_secret: OAUTH_CLIENT_SECRET, ... }
});

// After (SECURE - server handles secret):
fetch('/api/oauth/token', {
  body: { code, redirect_uri }
});
```

### 2. Hardcoded JWT Secret in .env
**File:** `.env`
**Issue:** JWT secret committed to version control
**Fix:**
- Replaced with placeholder value
- Added `.gitignore` to exclude `.env`
- Created `.env.example` with documentation
- Added production validation in `config/constants.js`

### 3. Weak Collabora Admin Password
**File:** `.env`
**Issue:** `COLLABORA_ADMIN_PASS=preoffice2024` was weak
**Fix:** Replaced with placeholder requiring production override

---

## High Security Fixes

### 1. Missing Authentication on API Endpoints
**Files:** `wopi-server/src/index.js`, `wopi-server/src/middleware/auth.js`
**Issue:** `/api/edit`, `/api/create`, `/api/recent` had no authentication
**Fix:** Added `requireBearerAuth` middleware to all API endpoints

```javascript
// Before:
app.post('/api/edit', async (req, res) => { ... });

// After:
app.post('/api/edit', editRateLimiter, requireBearerAuth, async (req, res) => { ... });
```

### 2. Unrestricted CORS Configuration
**File:** `wopi-server/src/middleware/security.js`
**Issue:** `app.use(cors())` allowed all origins
**Fix:** Created `corsMiddleware` with origin validation

```javascript
// Allowed origins from environment or defaults
const CORS_ALLOWED_ORIGINS = ['https://preoffice.site', 'https://predrive.eu', 'https://presuite.eu'];
```

### 3. Content Security Policy Disabled
**File:** `wopi-server/src/middleware/security.js`
**Issue:** `helmet({ contentSecurityPolicy: false })`
**Fix:** Added custom CSP via `securityHeaders` middleware

### 4. Path Traversal Vulnerability
**File:** `wopi-server/src/middleware/security.js`
**Issue:** fileId parameter decoded without validation
**Fix:** Added `validateFileId()` function

```javascript
function validateFileId(fileId) {
  // Check for path traversal attempts
  if (decoded.includes('..') || decoded.includes('\0')) {
    return { valid: false, error: 'Invalid path' };
  }
  // ... additional checks
}
```

### 5. Missing Security Headers (Nginx)
**File:** `nginx/nginx.conf`
**Issue:** No security headers configured
**Fix:** Added comprehensive security headers

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
```

### 6. Missing Security Headers (Application)
**File:** `wopi-server/src/middleware/security.js`
**Issue:** No application-level security headers
**Fix:** Created `securityHeaders` middleware

### 7. Insecure Token Storage
**File:** `branding/static/index.html`
**Issue:** Tokens stored in `localStorage` (accessible to XSS)
**Fix:** Changed to `sessionStorage` (still accessible, but clears on tab close)

### 8. Missing Input Sanitization
**File:** `wopi-server/src/middleware/security.js`
**Issue:** Filenames used without sanitization
**Fix:** Added `sanitizeFilename()` function

---

## Medium Security Fixes

### 1. No Rate Limiting
**File:** `wopi-server/src/middleware/rate-limiter.js` (NEW)
**Issue:** No protection against abuse/DoS
**Fix:** Added rate limiters for all endpoint types

| Endpoint Type | Limit | Window |
|--------------|-------|--------|
| API | 60 req | 1 min |
| Edit | 30 req | 1 min |
| Create | 20 req | 1 min |
| WOPI | 100 req | 1 min |

### 2. Verbose/Insecure Logging
**File:** `wopi-server/src/utils/logger.js` (NEW)
**Issue:** `console.log()` potentially exposing sensitive data
**Fix:** Created secure logger with data masking

```javascript
// Features:
- Masks email addresses (j***n@example.com)
- Masks UUIDs (12345678-****-****-****-************)
- Redacts JWT tokens (eyJ***[REDACTED]***)
- Structured JSON format in production
```

### 3. Long Token Expiry
**File:** `wopi-server/src/config/constants.js`
**Issue:** JWT tokens valid for 24 hours
**Fix:** Reduced to 4 hours

### 4. In-Memory Session Store
**File:** `wopi-server/src/index.js`
**Issue:** Sessions lost on restart, no cleanup
**Fix:** Added session cleanup interval (30 min)

### 5. Missing Request Timeouts
**Files:** Various
**Issue:** No timeouts on external API calls
**Fix:** Added timeouts (10-60s depending on operation)

### 6. Magic Numbers
**File:** `wopi-server/src/config/constants.js` (NEW)
**Issue:** Hardcoded values throughout
**Fix:** Centralized constants

---

## Low Security Fixes

### 1. Named Constants
**File:** `wopi-server/src/config/constants.js`
**Issue:** Magic numbers scattered throughout
**Fix:** Created named constants

```javascript
MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024;  // 100MB
SESSION_EXPIRY_MS = 4 * 60 * 60 * 1000;    // 4 hours
JWT_TOKEN_EXPIRY = '4h';
```

### 2. Structured Logging Format
**File:** `wopi-server/src/utils/logger.js`
**Issue:** Inconsistent log format
**Fix:** JSON structured logs in production

### 3. Improved Error Messages
**File:** `wopi-server/src/index.js`
**Issue:** Generic error responses
**Fix:** Consistent error format without exposing internals

### 4. Documentation
**Files:** Various
**Issue:** Missing security documentation
**Fix:** Added JSDoc comments, created this document

---

## Files Created

| File | Purpose |
|------|---------|
| `wopi-server/src/config/constants.js` | Centralized configuration with env validation |
| `wopi-server/src/middleware/rate-limiter.js` | Rate limiting middleware |
| `wopi-server/src/middleware/security.js` | Security headers and input validation |
| `wopi-server/src/middleware/auth.js` | Authentication middleware |
| `wopi-server/src/utils/logger.js` | Secure logging utility |
| `.env.example` | Environment variable documentation |
| `.gitignore` | Exclude sensitive files from git |
| `SECURITY-FIXES.md` | This document |

---

## Files Modified

| File | Changes |
|------|---------|
| `wopi-server/src/index.js` | Complete security refactor |
| `branding/static/index.html` | Removed hardcoded secret, use sessionStorage |
| `nginx/nginx.conf` | Added security headers |
| `.env` | Replaced secrets with placeholders |

---

## Environment Variables Required in Production

```bash
# REQUIRED - will throw error if not set in production
JWT_SECRET=<generate with: openssl rand -base64 64>
OAUTH_CLIENT_SECRET=<from PreSuite admin panel>
COLLABORA_ADMIN_PASS=<strong random password>

# RECOMMENDED
NODE_ENV=production
CORS_ORIGINS=https://preoffice.site,https://predrive.eu,https://presuite.eu
LOG_LEVEL=warn
```

---

## Security Checklist for Deployment

- [ ] Generate new JWT_SECRET (`openssl rand -base64 64`)
- [ ] Set OAUTH_CLIENT_SECRET from PreSuite admin
- [ ] Change COLLABORA_ADMIN_PASS to strong password
- [ ] Verify CORS_ORIGINS matches your domains
- [ ] Set NODE_ENV=production
- [ ] Test all authentication flows
- [ ] Verify rate limiting works
- [ ] Check security headers with securityheaders.com

---

## Next Steps

1. Deploy to staging for testing
2. Run security scan (e.g., OWASP ZAP)
3. Deploy to production
4. Monitor logs for any issues
5. Consider adding Redis for session storage (scalability)

---

*Generated by Claude Code Security Audit*
