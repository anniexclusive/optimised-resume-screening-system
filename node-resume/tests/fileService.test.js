/**
 * Unit tests for FileService
 * Tests file upload, validation, and cleanup operations
 */

const { FileService } = require('../services/fileService');
const fs = require('fs');
const path = require('path');

// Mock fs module
jest.mock('fs');

describe('FileService', () => {
  let fileService;
  const mockUploadDir = './uploads/resumes';

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock fs.existsSync to return true by default
    fs.existsSync.mockReturnValue(true);

    fileService = new FileService();
  });

  describe('Constructor', () => {
    it('should initialize with correct properties', () => {
      expect(fileService.uploadDir).toBeDefined();
      expect(fileService.maxFileSize).toBeDefined();
      expect(fileService.allowedExtensions).toBeDefined();
      expect(fileService.maxFiles).toBeDefined();
    });

    it('should create upload directory if it does not exist', () => {
      fs.existsSync.mockReturnValue(false);
      fs.mkdirSync = jest.fn();

      const newFileService = new FileService();

      expect(fs.mkdirSync).toHaveBeenCalledWith(
        expect.any(String),
        { recursive: true }
      );
    });
  });

  describe('ensureUploadDirectory', () => {
    it('should create directory if it does not exist', () => {
      fs.existsSync.mockReturnValue(false);
      fs.mkdirSync = jest.fn();

      fileService.ensureUploadDirectory();

      expect(fs.mkdirSync).toHaveBeenCalledWith(
        fileService.uploadDir,
        { recursive: true }
      );
    });

    it('should not create directory if it already exists', () => {
      fs.existsSync.mockReturnValue(true);
      fs.mkdirSync = jest.fn();

      fileService.ensureUploadDirectory();

      expect(fs.mkdirSync).not.toHaveBeenCalled();
    });
  });

  describe('validateFile', () => {
    it('should accept valid PDF files', (done) => {
      const file = { originalname: 'resume.pdf' };

      fileService.validateFile(file, (error, result) => {
        expect(error).toBeNull();
        expect(result).toBe(true);
        done();
      });
    });

    it('should reject DOCX files (not in allowed extensions)', (done) => {
      const file = { originalname: 'resume.docx' };

      fileService.validateFile(file, (error, result) => {
        expect(error).toBeInstanceOf(Error);
        expect(error.message).toContain('Invalid file type');
        done();
      });
    });

    it('should reject DOC files (not in allowed extensions)', (done) => {
      const file = { originalname: 'resume.doc' };

      fileService.validateFile(file, (error, result) => {
        expect(error).toBeInstanceOf(Error);
        expect(error.message).toContain('Invalid file type');
        done();
      });
    });

    it('should reject invalid file types', (done) => {
      const file = { originalname: 'malicious.exe' };

      fileService.validateFile(file, (error, result) => {
        expect(error).toBeInstanceOf(Error);
        expect(error.message).toContain('Invalid file type');
        done();
      });
    });

    it('should handle case-insensitive extensions', (done) => {
      const file = { originalname: 'resume.PDF' };

      fileService.validateFile(file, (error, result) => {
        expect(error).toBeNull();
        expect(result).toBe(true);
        done();
      });
    });
  });

  describe('getFilePaths', () => {
    it('should extract file paths from uploaded files', () => {
      const files = [
        { path: '/uploads/file1.pdf', originalname: 'file1.pdf' },
        { path: '/uploads/file2.pdf', originalname: 'file2.pdf' }
      ];

      const paths = fileService.getFilePaths(files);

      expect(paths).toEqual(['/uploads/file1.pdf', '/uploads/file2.pdf']);
    });

    it('should handle empty file array', () => {
      const paths = fileService.getFilePaths([]);
      expect(paths).toEqual([]);
    });
  });

  describe('createReadStreams', () => {
    it('should create read streams for existing files', () => {
      const mockStream = { on: jest.fn() };
      fs.existsSync.mockReturnValue(true);
      fs.createReadStream = jest.fn().mockReturnValue(mockStream);

      const filePaths = ['/uploads/file1.pdf', '/uploads/file2.pdf'];
      const streams = fileService.createReadStreams(filePaths);

      expect(streams).toHaveLength(2);
      expect(fs.createReadStream).toHaveBeenCalledTimes(2);
      expect(fs.createReadStream).toHaveBeenCalledWith('/uploads/file1.pdf');
      expect(fs.createReadStream).toHaveBeenCalledWith('/uploads/file2.pdf');
    });

    it('should throw error for non-existent files', () => {
      fs.existsSync.mockReturnValue(false);

      const filePaths = ['/uploads/nonexistent.pdf'];

      expect(() => {
        fileService.createReadStreams(filePaths);
      }).toThrow('File not found');
    });
  });

  describe('deleteFile', () => {
    it('should delete existing file', () => {
      fs.existsSync.mockReturnValue(true);
      fs.unlinkSync = jest.fn();

      const result = fileService.deleteFile('/uploads/file.pdf');

      expect(fs.unlinkSync).toHaveBeenCalledWith('/uploads/file.pdf');
      expect(result).toBe(true);
    });

    it('should return false for non-existent file', () => {
      fs.existsSync.mockReturnValue(false);
      fs.unlinkSync = jest.fn();

      const result = fileService.deleteFile('/uploads/nonexistent.pdf');

      expect(fs.unlinkSync).not.toHaveBeenCalled();
      expect(result).toBe(false);
    });

    it('should handle deletion errors gracefully', () => {
      fs.existsSync.mockReturnValue(true);
      fs.unlinkSync = jest.fn().mockImplementation(() => {
        throw new Error('Permission denied');
      });

      const result = fileService.deleteFile('/uploads/file.pdf');

      expect(result).toBe(false);
    });
  });

  describe('deleteFiles', () => {
    it('should delete multiple files', () => {
      fs.existsSync.mockReturnValue(true);
      fs.unlinkSync = jest.fn();

      const filePaths = [
        '/uploads/file1.pdf',
        '/uploads/file2.pdf',
        '/uploads/file3.pdf'
      ];

      const deletedCount = fileService.deleteFiles(filePaths);

      expect(fs.unlinkSync).toHaveBeenCalledTimes(3);
      expect(deletedCount).toBe(3);
    });

    it('should handle partial deletion failures', () => {
      let callCount = 0;
      fs.existsSync.mockReturnValue(true);
      fs.unlinkSync = jest.fn().mockImplementation(() => {
        callCount++;
        if (callCount === 2) {
          throw new Error('Permission denied');
        }
      });

      const filePaths = ['/uploads/file1.pdf', '/uploads/file2.pdf', '/uploads/file3.pdf'];

      const deletedCount = fileService.deleteFiles(filePaths);

      expect(deletedCount).toBe(2); // 2 out of 3 succeeded
    });
  });

  describe('cleanupOldFiles', () => {
    it('should delete files older than specified age', () => {
      const now = Date.now();
      const oldFileTime = now - (25 * 60 * 60 * 1000); // 25 hours ago
      const newFileTime = now - (1 * 60 * 60 * 1000);   // 1 hour ago

      fs.readdirSync = jest.fn().mockReturnValue(['old-file.pdf', 'new-file.pdf']);
      fs.statSync = jest.fn()
        .mockReturnValueOnce({ mtimeMs: oldFileTime })  // old file
        .mockReturnValueOnce({ mtimeMs: newFileTime }); // new file

      fs.existsSync.mockReturnValue(true);
      fs.unlinkSync = jest.fn();

      const deletedCount = fileService.cleanupOldFiles(24);

      expect(deletedCount).toBe(1); // Only old file deleted
      expect(fs.unlinkSync).toHaveBeenCalledTimes(1);
    });

    it('should not delete recent files', () => {
      const now = Date.now();
      const recentTime = now - (1 * 60 * 60 * 1000); // 1 hour ago

      fs.readdirSync = jest.fn().mockReturnValue(['recent-file.pdf']);
      fs.statSync = jest.fn().mockReturnValue({ mtimeMs: recentTime });
      fs.unlinkSync = jest.fn();

      const deletedCount = fileService.cleanupOldFiles(24);

      expect(deletedCount).toBe(0);
      expect(fs.unlinkSync).not.toHaveBeenCalled();
    });

    it('should handle cleanup errors gracefully', () => {
      fs.readdirSync = jest.fn().mockImplementation(() => {
        throw new Error('Read directory failed');
      });

      const deletedCount = fileService.cleanupOldFiles(24);

      expect(deletedCount).toBe(0);
    });
  });

  describe('getMulterStorage', () => {
    it('should return multer storage configuration', () => {
      const storage = fileService.getMulterStorage();
      expect(storage).toBeDefined();
    });
  });

  describe('getUploadMiddleware', () => {
    it('should return multer upload middleware', () => {
      const middleware = fileService.getUploadMiddleware();
      expect(middleware).toBeDefined();
    });
  });
});
