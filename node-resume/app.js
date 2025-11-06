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
  max: 100 // Limit each IP to 100 requests per windowMs
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
  console.log(`${req.method} ${req.path} - ${req.ip}`);
  next();
});

// Routes
const resume = require('./resume');

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    service: 'resume-screening-backend',
    version: '1.0.0',
    environment: config.env,
    timestamp: new Date().toISOString()
  });
});

// API route
app.get('/api', (req, res) => {
  res.json({ message: 'Hello World from Node.js backend!' });
});

app.use(resume);

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Route ${req.method} ${req.path} not found`
  });
});

// Global error handler
app.use((err, req, res, next) => {
  console.error('Error:', err.message);

  res.status(err.status || 500).json({
    error: 'Internal Server Error',
    message: config.env === 'production' ? 'An unexpected error occurred' : err.message
  });
});

// Start server
const server = app.listen(config.server.port, () => {
  console.log(`Server is running on http://${config.server.host}:${config.server.port}`);
  console.log(`Environment: ${config.env}`);
  console.log(`Python API: ${config.pythonApi.baseUrl}`);
});

// Graceful shutdown
const gracefulShutdown = (signal) => {
  console.log(`${signal} received. Shutting down gracefully...`);
  server.close(() => {
    console.log('Server closed');
    process.exit(0);
  });
};

// Handle shutdown signals
process.on('SIGTERM', gracefulShutdown);
process.on('SIGINT', gracefulShutdown);

module.exports = app;
