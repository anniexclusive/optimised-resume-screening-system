/**
 * Resume Screening Backend
 * Main Express application with security, logging, and error handling
 */

const express = require('express');
const path = require('path');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const config = require('./config/api.config');
const logger = require('./utils/logger');
const { apiKeyAuth, isAuthConfigured } = require('./middleware/auth');

const app = express();

// Security: Helmet middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true
  }
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
  handler: (req, res) => {
    logger.warn(`Rate limit exceeded for IP: ${req.ip}`);
    res.status(429).json({
      error: 'Too Many Requests',
      message: 'Too many requests from this IP, please try again later.'
    });
  }
});

// Apply rate limiting to API routes
app.use('/upload', limiter);

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'client/build')));

// CORS middleware
app.use(cors({
  origin: config.cors.origin,
  credentials: config.cors.credentials
}));

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  logger.info(`${req.method} ${req.path}`, {
    ip: req.ip,
    userAgent: req.get('user-agent')
  });
  next();
});

// API Key Authentication middleware (applies to all routes except health check)
app.use(apiKeyAuth);

// Routes
const resume = require('./resume');
const { httpClient } = require('./services');

// Health check endpoint with circuit breaker status
app.get('/health', (req, res) => {
  const circuitBreakerState = httpClient.getCircuitBreakerState();

  res.status(200).json({
    status: 'healthy',
    service: 'resume-screening-backend',
    version: '1.0.0',
    environment: config.env,
    timestamp: new Date().toISOString(),
    circuitBreaker: circuitBreakerState  // SRE: Expose circuit breaker state for monitoring
  });
});

// API route
app.get('/api', (req, res) => {
  res.json({ message: 'Hello World from Node.js backend!' });
});

app.use(resume);

// 404 handler
app.use((req, res) => {
  logger.warn(`404 - Route not found: ${req.method} ${req.path}`);
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`
  });
});

// Global error handler
app.use((err, req, res, next) => {
  logger.error('Unhandled error:', {
    error: err.message,
    stack: err.stack,
    path: req.path,
    method: req.method
  });

  // Don't leak error details in production
  const message = config.env === 'production'
    ? 'An unexpected error occurred'
    : err.message;

  res.status(err.status || 500).json({
    error: 'Internal Server Error',
    message: message,
    ...(config.env !== 'production' && { stack: err.stack })
  });
});

// Start server
const server = app.listen(config.server.port, () => {
  logger.info(`Server is running on http://${config.server.host}:${config.server.port}`);
  logger.info(`Environment: ${config.env}`);
  logger.info(`Python API: ${config.pythonApi.baseUrl}`);

  // Check authentication configuration
  isAuthConfigured();
});

// Graceful shutdown
const gracefulShutdown = (signal) => {
  logger.info(`${signal} received. Starting graceful shutdown...`);

  server.close(() => {
    logger.info('HTTP server closed');

    // Close database connections, cleanup resources here
    // For example: await db.close();

    logger.info('Graceful shutdown completed');
    process.exit(0);
  });

  // Force shutdown after 10 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 10000);
};

// Handle shutdown signals
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT', () => gracefulShutdown('SIGINT'));

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
  logger.error('Uncaught Exception:', { error: error.message, stack: error.stack });
  gracefulShutdown('uncaughtException');
});

// Handle unhandled promise rejections
process.on('unhandledRejection', (reason, promise) => {
  logger.error('Unhandled Rejection:', { reason, promise });
  gracefulShutdown('unhandledRejection');
});

module.exports = app;
