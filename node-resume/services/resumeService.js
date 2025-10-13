/**
 * Resume Service
 * Business logic for resume screening operations
 */

const FormData = require('form-data');
const fs = require('fs');
const config = require('../config/api.config');

class ResumeService {
  constructor(httpClientInstance, fileServiceInstance) {
    this.httpClient = httpClientInstance;
    this.fileService = fileServiceInstance;
    this.pythonApiUrl = `${config.pythonApi.baseUrl}${config.pythonApi.endpoints.predictBert}`;
  }

  /**
   * Process resume screening request
   *
   * @param {Object} jobData - Job requirements
   * @param {Array} files - Uploaded resume files
   * @returns {Promise<Object>} - Screening results
   */
  async screenResumes(jobData, files) {
    try {
      console.log('[ResumeService] Starting resume screening process');

      // Validate input
      this.validateScreeningInput(jobData, files);

      // Prepare form data
      const formData = this.prepareFormData(jobData, files);

      // Send to Python API
      console.log(`[ResumeService] Sending ${files.length} resumes to Python API`);
      const results = await this.httpClient.postFormData(this.pythonApiUrl, formData);

      console.log('[ResumeService] Received results from Python API');
      return results;

    } catch (error) {
      console.error('[ResumeService] Error screening resumes:', error);
      throw this.handleError(error);
    }
  }

  /**
   * Validate screening input
   */
  validateScreeningInput(jobData, files) {
    if (!jobData) {
      throw new Error('Job data is required');
    }

    if (!files || files.length === 0) {
      throw new Error('At least one resume file is required');
    }

    const maxFiles = config.upload.maxFiles;
    if (files.length > maxFiles) {
      throw new Error(`Maximum ${maxFiles} files allowed`);
    }

    // Validate required job fields
    const requiredFields = ['jobDescription', 'skills', 'education', 'experience'];
    const missingFields = requiredFields.filter(field => !jobData[field]);

    if (missingFields.length > 0) {
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }
  }

  /**
   * Prepare form data for Python API
   */
  prepareFormData(jobData, files) {
    const formData = new FormData();

    // Append resume files
    files.forEach(file => {
      const stream = fs.createReadStream(file.path);
      formData.append('resumes', stream, {
        filename: file.originalname || file.filename
      });
    });

    // Append job details
    formData.append('job_description', jobData.jobDescription);
    formData.append('skills', jobData.skills);
    formData.append('education', jobData.education);
    formData.append('experience', jobData.experience);

    return formData;
  }

  /**
   * Parse and format skills
   */
  parseSkills(skillsString) {
    if (!skillsString) return [];

    return skillsString
      .split(',')
      .map(skill => skill.trim())
      .filter(skill => skill.length > 0);
  }

  /**
   * Handle errors with proper formatting
   */
  handleError(error) {
    if (error.status) {
      // Error from HTTP client
      return {
        message: error.message || 'An error occurred while processing resumes',
        status: error.status,
        details: error.data
      };
    }

    // Generic error
    return {
      message: error.message || 'Internal server error',
      status: 500,
      details: null
    };
  }

  /**
   * Clean up uploaded files after processing
   */
  async cleanupFiles(files) {
    try {
      files.forEach(file => {
        if (fs.existsSync(file.path)) {
          fs.unlinkSync(file.path);
        }
      });
      console.log('[ResumeService] Cleaned up uploaded files');
    } catch (error) {
      console.error('[ResumeService] Error cleaning up files:', error.message);
    }
  }
}

module.exports = {
  ResumeService
};
