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
            predictBert: '/predictbert',
            health: '/health',
            ready: '/ready'
        },
        // Timeout: 2 minutes for ML processing (BERT inference can take 30-60s for 10 resumes)
        timeout: parseInt(process.env.API_TIMEOUT) || 120000,
        // Retry configuration for transient failures
        retryConfig: {
            maxRetries: parseInt(process.env.API_MAX_RETRIES) || 3,
            retryDelay: parseInt(process.env.API_RETRY_DELAY) || 1000,
            retryableStatuses: [408, 429, 500, 502, 503, 504], // Retry on transient errors
            exponentialBackoff: true
        }
    },

    // File Upload Configuration
    upload: {
        directory: process.env.UPLOAD_DIR || 'uploads',
        maxFileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB
        allowedExtensions: ['.pdf'],
        maxFiles: parseInt(process.env.MAX_FILES) || 10
    },

    // CORS Configuration
    // SRE Best Practice: Support multiple origins for different environments
    // Format: CORS_ORIGINS=http://localhost:3000,https://app.example.com,https://staging.example.com
    cors: {
        origin: function(origin, callback) {
            const allowedOrigins = process.env.CORS_ORIGINS
                ? process.env.CORS_ORIGINS.split(',').map(o => o.trim())
                : ['http://localhost:3000'];

            // Allow requests with no origin (like mobile apps, curl, Postman)
            if (!origin) return callback(null, true);

            if (allowedOrigins.indexOf(origin) !== -1 || allowedOrigins.includes('*')) {
                callback(null, true);
            } else {
                callback(new Error('Not allowed by CORS'));
            }
        },
        credentials: true,
        optionsSuccessStatus: 200, // Some legacy browsers choke on 204
        maxAge: 86400 // Cache preflight requests for 24 hours
    }
};
