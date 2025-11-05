/**
 * Unit tests for ResumeService
 * Tests resume screening business logic
 */

// Mock dependencies before importing ResumeService
jest.mock('fs');
jest.mock('form-data');

const { ResumeService } = require('../services/resumeService');
const FormData = require('form-data');
const fs = require('fs');

describe('ResumeService', () => {
  let resumeService;
  let mockHttpClient;
  let mockFileService;

  beforeEach(() => {
    jest.clearAllMocks();

    // Mock HTTP client with all methods including new resilient ones
    mockHttpClient = {
      postFormData: jest.fn(),
      postFormDataWithRetry: jest.fn(),
      postFormDataResilient: jest.fn(),
      getCircuitBreakerState: jest.fn(() => ({ state: 'CLOSED', failureCount: 0 }))
    };

    // Mock file service
    mockFileService = {
      deleteFiles: jest.fn()
    };

    resumeService = new ResumeService(mockHttpClient, mockFileService);
  });

  describe('Constructor', () => {
    it('should initialize with dependencies', () => {
      expect(resumeService.httpClient).toBe(mockHttpClient);
      expect(resumeService.fileService).toBe(mockFileService);
      expect(resumeService.pythonApiUrl).toBeDefined();
    });
  });

  describe('validateScreeningInput', () => {
    const validJobData = {
      jobDescription: 'Python developer needed',
      skills: 'Python, Flask',
      education: 'Bachelor degree',
      experience: '3 years'
    };

    const validFiles = [
      { path: '/uploads/resume1.pdf', originalname: 'resume1.pdf' }
    ];

    it('should validate correct input', () => {
      expect(() => {
        resumeService.validateScreeningInput(validJobData, validFiles);
      }).not.toThrow();
    });

    it('should throw error if jobData is missing', () => {
      expect(() => {
        resumeService.validateScreeningInput(null, validFiles);
      }).toThrow('Job data is required');
    });

    it('should throw error if files are missing', () => {
      expect(() => {
        resumeService.validateScreeningInput(validJobData, []);
      }).toThrow('At least one resume file is required');
    });

    it('should throw error if files parameter is null', () => {
      expect(() => {
        resumeService.validateScreeningInput(validJobData, null);
      }).toThrow('At least one resume file is required');
    });

    it('should throw error for missing jobDescription', () => {
      const invalidJobData = { ...validJobData };
      delete invalidJobData.jobDescription;

      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('Missing required fields: jobDescription');
    });

    it('should throw error for missing skills', () => {
      const invalidJobData = { ...validJobData };
      delete invalidJobData.skills;

      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('Missing required fields: skills');
    });

    it('should throw error for missing education', () => {
      const invalidJobData = { ...validJobData };
      delete invalidJobData.education;

      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('Missing required fields: education');
    });

    it('should throw error for missing experience', () => {
      const invalidJobData = { ...validJobData };
      delete invalidJobData.experience;

      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('Missing required fields: experience');
    });

    it('should throw error for multiple missing fields', () => {
      const invalidJobData = {
        jobDescription: 'Test'
      };

      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('Missing required fields');
      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('skills');
      expect(() => {
        resumeService.validateScreeningInput(invalidJobData, validFiles);
      }).toThrow('education');
    });

    it('should throw error if too many files uploaded', () => {
      const tooManyFiles = Array(101).fill({
        path: '/uploads/resume.pdf',
        originalname: 'resume.pdf'
      });

      expect(() => {
        resumeService.validateScreeningInput(validJobData, tooManyFiles);
      }).toThrow('Maximum');
    });
  });

  describe('prepareFormData', () => {
    const jobData = {
      jobDescription: 'Python developer',
      skills: 'Python, Flask',
      education: 'BS Computer Science',
      experience: '3 years'
    };

    const files = [
      { path: '/uploads/resume1.pdf', originalname: 'resume1.pdf' },
      { path: '/uploads/resume2.pdf', filename: 'resume2.pdf' }
    ];

    beforeEach(() => {
      // Mock fs.createReadStream
      fs.createReadStream = jest.fn().mockReturnValue('mock-stream');
    });

    it('should create FormData with job details', () => {
      const formData = resumeService.prepareFormData(jobData, files);

      expect(formData.append).toHaveBeenCalledWith('job_description', jobData.jobDescription);
      expect(formData.append).toHaveBeenCalledWith('skills', jobData.skills);
      expect(formData.append).toHaveBeenCalledWith('education', jobData.education);
      expect(formData.append).toHaveBeenCalledWith('experience', jobData.experience);
    });

    it('should create read streams for all files', () => {
      resumeService.prepareFormData(jobData, files);

      expect(fs.createReadStream).toHaveBeenCalledWith('/uploads/resume1.pdf');
      expect(fs.createReadStream).toHaveBeenCalledWith('/uploads/resume2.pdf');
    });

    it('should append files to FormData with correct filenames', () => {
      const formData = resumeService.prepareFormData(jobData, files);

      // Should use originalname if available
      expect(formData.append).toHaveBeenCalledWith(
        'resumes',
        'mock-stream',
        { filename: 'resume1.pdf' }
      );

      // Should fall back to filename if originalname not available
      expect(formData.append).toHaveBeenCalledWith(
        'resumes',
        'mock-stream',
        { filename: 'resume2.pdf' }
      );
    });
  });

  describe('screenResumes', () => {
    const jobData = {
      jobDescription: 'Python developer',
      skills: 'Python, Flask',
      education: 'BS',
      experience: '3 years'
    };

    const files = [
      { path: '/uploads/resume.pdf', originalname: 'resume.pdf' }
    ];

    beforeEach(() => {
      // Mock fs.createReadStream
      fs.createReadStream = jest.fn().mockReturnValue('mock-stream');
    });

    it('should successfully screen resumes', async () => {
      const mockResults = [
        { filename: 'resume.pdf', ts: 85, ss: 35, ex: 25, ed: 15, ge: 10 }
      ];

      mockHttpClient.postFormDataResilient.mockResolvedValue(mockResults);

      const results = await resumeService.screenResumes(jobData, files);

      expect(mockHttpClient.postFormDataResilient).toHaveBeenCalled();
      expect(results).toEqual(mockResults);
    });

    it('should validate input before processing', async () => {
      const invalidJobData = { jobDescription: 'Test' }; // Missing required fields

      try {
        await resumeService.screenResumes(invalidJobData, files);
        // If it doesn't throw, fail the test
        fail('Expected to throw an error');
      } catch (error) {
        expect(error.message).toContain('Missing required fields');
      }

      expect(mockHttpClient.postFormDataResilient).not.toHaveBeenCalled();
    });

    it('should handle HTTP client errors', async () => {
      const error = {
        status: 500,
        message: 'Internal server error',
        data: { detail: 'Processing failed' }
      };

      mockHttpClient.postFormDataResilient.mockRejectedValue(error);

      await expect(
        resumeService.screenResumes(jobData, files)
      ).rejects.toMatchObject({
        message: 'Internal server error',
        status: 500
      });
    });

    it('should handle generic errors', async () => {
      const error = new Error('Unexpected error');
      mockHttpClient.postFormDataResilient.mockRejectedValue(error);

      await expect(
        resumeService.screenResumes(jobData, files)
      ).rejects.toMatchObject({
        message: 'Unexpected error',
        status: 500
      });
    });
  });

  describe('parseSkills', () => {
    it('should parse comma-separated skills', () => {
      const skills = resumeService.parseSkills('Python, JavaScript, React');
      expect(skills).toEqual(['Python', 'JavaScript', 'React']);
    });

    it('should trim whitespace from skills', () => {
      const skills = resumeService.parseSkills('  Python  ,  JavaScript  ,  React  ');
      expect(skills).toEqual(['Python', 'JavaScript', 'React']);
    });

    it('should filter out empty skills', () => {
      const skills = resumeService.parseSkills('Python, , JavaScript, , React');
      expect(skills).toEqual(['Python', 'JavaScript', 'React']);
    });

    it('should handle empty string', () => {
      const skills = resumeService.parseSkills('');
      expect(skills).toEqual([]);
    });

    it('should handle null input', () => {
      const skills = resumeService.parseSkills(null);
      expect(skills).toEqual([]);
    });

    it('should handle undefined input', () => {
      const skills = resumeService.parseSkills(undefined);
      expect(skills).toEqual([]);
    });
  });

  describe('handleError', () => {
    it('should format HTTP client errors', () => {
      const error = {
        status: 400,
        message: 'Bad request',
        data: { field: 'error detail' }
      };

      const formatted = resumeService.handleError(error);

      expect(formatted).toEqual({
        message: 'Bad request',
        status: 400,
        details: { field: 'error detail' }
      });
    });

    it('should format generic errors', () => {
      const error = new Error('Something went wrong');

      const formatted = resumeService.handleError(error);

      expect(formatted).toEqual({
        message: 'Something went wrong',
        status: 500,
        details: null
      });
    });

    it('should provide default message for errors without message', () => {
      const error = { status: 500 };

      const formatted = resumeService.handleError(error);

      expect(formatted.message).toBe('An error occurred while processing resumes');
    });
  });

  describe('cleanupFiles', () => {
    beforeEach(() => {
      fs.existsSync = jest.fn().mockReturnValue(true);
      fs.unlinkSync = jest.fn();
    });

    it('should delete all uploaded files', async () => {
      const files = [
        { path: '/uploads/file1.pdf' },
        { path: '/uploads/file2.pdf' }
      ];

      await resumeService.cleanupFiles(files);

      expect(fs.unlinkSync).toHaveBeenCalledWith('/uploads/file1.pdf');
      expect(fs.unlinkSync).toHaveBeenCalledWith('/uploads/file2.pdf');
    });

    it('should skip non-existent files', async () => {
      fs.existsSync.mockReturnValue(false);

      const files = [{ path: '/uploads/nonexistent.pdf' }];

      await resumeService.cleanupFiles(files);

      expect(fs.unlinkSync).not.toHaveBeenCalled();
    });

    it('should handle cleanup errors gracefully', async () => {
      fs.unlinkSync.mockImplementation(() => {
        throw new Error('Permission denied');
      });

      const files = [{ path: '/uploads/file.pdf' }];

      // Should not throw
      await expect(resumeService.cleanupFiles(files)).resolves.toBeUndefined();
    });

    it('should handle empty file array', async () => {
      await expect(resumeService.cleanupFiles([])).resolves.toBeUndefined();
      expect(fs.unlinkSync).not.toHaveBeenCalled();
    });
  });
});
