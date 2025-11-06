/**
 * File Service
 * Handles file upload, validation, and processing
 */

const fs = require('fs');
const path = require('path');
const multer = require('multer');
const sanitizeFilename = require('sanitize-filename');
const config = require('../config/api.config');

class FileService {
  constructor() {
    this.uploadDir = config.upload.directory;
    this.maxFileSize = config.upload.maxFileSize;
    this.allowedExtensions = config.upload.allowedExtensions;
    this.maxFiles = config.upload.maxFiles;

    // Ensure upload directory exists
    this.ensureUploadDirectory();
  }

  /**
   * Ensure upload directory exists
   */
  ensureUploadDirectory() {
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
      console.log(`[FileService] Created upload directory: ${this.uploadDir}`);
    }
  }

  /**
   * Configure multer storage
   */
  getMulterStorage() {
    return multer.diskStorage({
      destination: (req, file, cb) => {
        this.ensureUploadDirectory();
        cb(null, this.uploadDir);
      },
      filename: (req, file, cb) => {
        const safeFilename = sanitizeFilename(file.originalname);
        cb(null, safeFilename);
      }
    });
  }

  /**
   * Get multer upload middleware
   */
  getUploadMiddleware() {
    const storage = this.getMulterStorage();

    return multer({
      storage,
      limits: {
        fileSize: this.maxFileSize,
        files: this.maxFiles
      },
      fileFilter: (req, file, cb) => {
        this.validateFile(file, cb);
      }
    });
  }

  /**
   * Validate uploaded file
   */
  validateFile(file, callback) {
    const ext = path.extname(file.originalname).toLowerCase();

    if (!this.allowedExtensions.includes(ext)) {
      return callback(
        new Error(`Invalid file type. Allowed: ${this.allowedExtensions.join(', ')}`)
      );
    }

    callback(null, true);
  }

  /**
   * Get file paths from uploaded files
   */
  getFilePaths(files) {
    return files.map(file => file.path);
  }

  /**
   * Create read streams for files
   */
  createReadStreams(filePaths) {
    return filePaths.map(filePath => {
      if (!fs.existsSync(filePath)) {
        throw new Error(`File not found: ${filePath}`);
      }
      return fs.createReadStream(filePath);
    });
  }

  /**
   * Delete file
   */
  deleteFile(filePath) {
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        return true;
      }
      return false;
    } catch (error) {
      console.error(`[FileService] Error deleting file ${filePath}:`, error.message);
      return false;
    }
  }

  /**
   * Delete multiple files
   */
  deleteFiles(filePaths) {
    const results = filePaths.map(filePath => this.deleteFile(filePath));
    const deletedCount = results.filter(r => r).length;
    console.log(`[FileService] Deleted ${deletedCount}/${filePaths.length} files`);
    return deletedCount;
  }

  /**
   * Clean up old files in upload directory
   */
  cleanupOldFiles(maxAgeHours = 24) {
    const now = Date.now();
    const maxAge = maxAgeHours * 60 * 60 * 1000;

    try {
      const files = fs.readdirSync(this.uploadDir);
      let deletedCount = 0;

      files.forEach(file => {
        const filePath = path.join(this.uploadDir, file);
        const stats = fs.statSync(filePath);
        const age = now - stats.mtimeMs;

        if (age > maxAge) {
          this.deleteFile(filePath);
          deletedCount++;
        }
      });

      console.log(`[FileService] Cleanup: deleted ${deletedCount} old files`);
      return deletedCount;
    } catch (error) {
      console.error('[FileService] Cleanup error:', error.message);
      return 0;
    }
  }
}

// Export singleton instance
const fileService = new FileService();

module.exports = {
  FileService,
  fileService
};
