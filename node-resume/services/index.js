/**
 * Services Index
 * Central export for all services
 */

const { HttpClient, httpClient } = require('./httpClient');
const { FileService, fileService } = require('./fileService');
const { ResumeService, resumeService } = require('./resumeService');

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
