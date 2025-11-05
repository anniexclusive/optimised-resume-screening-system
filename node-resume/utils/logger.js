/**
 * Logger utility using Winston
 * Provides structured logging with different levels
 *
 * SRE Best Practice: Use stdout/stderr for containerized applications
 * - Docker/Kubernetes capture stdout/stderr automatically
 * - Centralized logging systems (ELK, Datadog, CloudWatch) integrate with container logs
 * - File logging in containers is ephemeral and gets lost on container restart
 */

const winston = require('winston');

// JSON format for production (machine-readable, structured)
const jsonFormat = winston.format.combine(
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.errors({ stack: true }),
  winston.format.splat(),
  winston.format.json()
);

// Human-readable format for development
const developmentFormat = winston.format.combine(
  winston.format.colorize(),
  winston.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss' }),
  winston.format.printf(({ timestamp, level, message, ...metadata }) => {
    let msg = `${timestamp} [${level}]: ${message}`;
    if (Object.keys(metadata).length > 0) {
      msg += ` ${JSON.stringify(metadata)}`;
    }
    return msg;
  })
);

// Determine format based on environment
const isProduction = process.env.NODE_ENV === 'production';
const format = isProduction ? jsonFormat : developmentFormat;

/**
 * Create logger instance
 *
 * SRE Configuration:
 * - Production: JSON to stdout/stderr (captured by Docker logging drivers)
 * - Development: Colorized human-readable format
 * - No file transports (antipattern in containers)
 */
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format,
  defaultMeta: {
    service: 'resume-screening-backend',
    environment: process.env.NODE_ENV || 'development',
    hostname: process.env.HOSTNAME || 'unknown'
  },
  transports: [
    // stdout for info and above (captured by Docker/k8s)
    new winston.transports.Console({
      level: 'info',
      stderrLevels: ['error'], // errors go to stderr
    })
  ],
  // Exit on error is false to prevent crashes on logging errors
  exitOnError: false
});

// Log startup configuration
logger.info('Logger initialized', {
  logLevel: logger.level,
  format: isProduction ? 'json' : 'development',
  outputStreams: ['stdout', 'stderr']
});

module.exports = logger;
