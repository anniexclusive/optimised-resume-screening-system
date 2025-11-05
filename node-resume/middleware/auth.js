/**
 * API Key Authentication Middleware
 * Provides basic API key security for production endpoints
 */

const logger = require('../utils/logger');

// Load API keys from environment variable (comma-separated)
// Example: API_KEYS=key1,key2,key3
const API_KEYS = new Set(
  process.env.API_KEYS?.split(',').map(key => key.trim()).filter(key => key) || []
);

// Flag to enable/disable auth (for development)
const AUTH_ENABLED = process.env.ENABLE_AUTH !== 'false';

/**
 * API Key Authentication Middleware
 * Checks for X-API-Key header and validates against configured keys
 */
const apiKeyAuth = (req, res, next) => {
  // Skip auth if disabled (development only)
  if (!AUTH_ENABLED) {
    logger.debug('[Auth] Authentication disabled');
    return next();
  }

  // Skip auth for health check endpoint
  if (req.path === '/health') {
    return next();
  }

  // Get API key from header
  const apiKey = req.header('X-API-Key');

  // Check if API key is provided
  if (!apiKey) {
    logger.warn('[Auth] Missing API key', {
      ip: req.ip,
      path: req.path,
      method: req.method
    });

    return res.status(401).json({
      error: 'Unauthorized',
      message: 'API key is required. Please provide X-API-Key header.'
    });
  }

  // Validate API key
  if (!API_KEYS.has(apiKey)) {
    logger.warn('[Auth] Invalid API key attempt', {
      ip: req.ip,
      path: req.path,
      method: req.method,
      keyPrefix: apiKey.substring(0, 8) + '...' // Log only prefix for security
    });

    return res.status(403).json({
      error: 'Forbidden',
      message: 'Invalid API key'
    });
  }

  // API key is valid
  logger.debug('[Auth] API key validated successfully', {
    ip: req.ip,
    path: req.path
  });

  next();
};

/**
 * Check if authentication is properly configured
 */
const isAuthConfigured = () => {
  if (!AUTH_ENABLED) {
    logger.warn('[Auth] Authentication is DISABLED - not recommended for production');
    return false;
  }

  if (API_KEYS.size === 0) {
    logger.error('[Auth] No API keys configured! Set API_KEYS environment variable.');
    return false;
  }

  logger.info(`[Auth] Authentication enabled with ${API_KEYS.size} API key(s)`);
  return true;
};

module.exports = {
  apiKeyAuth,
  isAuthConfigured
};
