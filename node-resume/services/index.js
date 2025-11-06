/**
 * Services Index
 * Central export for all services
 */

const { FileService, fileService } = require('./fileService');
const { ResumeService } = require('./resumeService');

// Create ResumeService singleton with injected dependencies
const resumeService = new ResumeService(fileService);

module.exports = {
  // Classes
  FileService,
  ResumeService,

  // Singleton instances
  fileService,
  resumeService
};
