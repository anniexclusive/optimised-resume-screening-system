/**
 * API Configuration
 * Centralized configuration for all external API endpoints and app settings
 */

const config = {
  // Environment
  env: process.env.NODE_ENV || 'development',

  // Server Configuration
  server: {
    port: process.env.PORT || 3001,
    host: process.env.HOST || 'localhost'
  },

  // Python API Configuration
  pythonApi: {
    baseUrl: process.env.PYTHON_API_URL || 'http://localhost:5000',
    endpoints: {
      predictBert: '/predictbert',
      health: '/health'
    },
    timeout: parseInt(process.env.API_TIMEOUT) || 30000 // 30 seconds
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
    origin: process.env.CORS_ORIGIN || '*',
    credentials: true
  }
};

// Helper function to get full Python API URL
config.getPythonApiUrl = (endpoint) => {
  return `${config.pythonApi.baseUrl}${endpoint}`;
};

module.exports = config;
