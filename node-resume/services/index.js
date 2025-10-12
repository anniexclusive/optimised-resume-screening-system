/**
 * Services Index
 * Central export for all services with proper dependency injection
 */

const { HttpClient, httpClient } = require('./httpClient');
const { FileService, fileService } = require('./fileService');
const { ResumeService } = require('./resumeService');

// Create ResumeService singleton with injected dependencies
const resumeService = new ResumeService(httpClient, fileService);

module.exports = {
  // Classes
  HttpClient,
  FileService,
  ResumeService,

  // Singleton instances
  httpClient,
  fileService,
  resumeService
};
