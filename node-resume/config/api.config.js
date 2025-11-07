/**
 * API Configuration
 * Centralizes all configuration for the Node.js backend
 * Following SOLID principles - Single Responsibility & Open/Closed
 */

module.exports = {
  // Environment
  env: process.env.NODE_ENV || 'development',

  // Server Configuration
  server: {
    port: parseInt(process.env.PORT) || 3001,
    host: process.env.HOST || 'localhost'
  },

  // Python API Configuration
  pythonApi: {
    baseUrl: process.env.PYTHON_API_URL || 'http://localhost:5000',
    endpoints: {
      predictBert: '/predictbert'
    },
    timeout: parseInt(process.env.API_TIMEOUT) || 120000 // 2 minutes for ML processing
  },

  // File Upload Configuration
  upload: {
    directory: process.env.UPLOAD_DIR || 'uploads',
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB
    allowedExtensions: ['.pdf'],
    maxFiles: parseInt(process.env.MAX_FILES) || 10
  },

  // CORS Configuration
  cors: {
    origin: process.env.CORS_ORIGIN || 'http://localhost:3000',
    credentials: true
  }
};
