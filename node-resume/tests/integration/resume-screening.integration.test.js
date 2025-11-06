/**
 * Integration Tests for Resume Screening Flow
 * Tests the complete workflow from file upload to Python API integration
 */

const request = require('supertest');
const path = require('path');
const fs = require('fs');

// Note: These tests require the app and Python API to be running
// Run with: npm test -- tests/integration/
// Or skip in CI with: npm test -- --testPathIgnorePatterns=integration

describe('Resume Screening Integration Tests', () => {
  let app;

  beforeAll(() => {
    // Import app after setting test environment
    process.env.NODE_ENV = 'test';
    // Note: Uncomment when ready to run integration tests
    // app = require('../../app');
  });

  describe('POST /resume-screening', () => {
    it.skip('should successfully screen a valid resume', async () => {
      // Create a test PDF file
      const testPdfPath = path.join(__dirname, 'fixtures', 'test-resume.pdf');

      const response = await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Python developer with Flask experience')
        .field('skills', 'Python, Flask, Machine Learning')
        .field('education', 'Bachelor of Science in Computer Science')
        .field('experience', '3 years')
        .attach('resumes', testPdfPath)
        .expect('Content-Type', /json/)
        .expect(200);

      // Verify response structure
      expect(response.body).toBeInstanceOf(Array);
      expect(response.body.length).toBeGreaterThan(0);

      const result = response.body[0];
      expect(result).toHaveProperty('filename');
      expect(result).toHaveProperty('ts'); // Total score
      expect(result).toHaveProperty('ss'); // Skills score
      expect(result).toHaveProperty('ex'); // Experience score
      expect(result).toHaveProperty('ed'); // Education score
      expect(result).toHaveProperty('ge'); // General score
      expect(result).toHaveProperty('explanation');

      // Verify score ranges
      expect(result.ts).toBeGreaterThanOrEqual(0);
      expect(result.ts).toBeLessThanOrEqual(100);
    });

    it.skip('should handle multiple resume uploads', async () => {
      const testPdf1 = path.join(__dirname, 'fixtures', 'resume1.pdf');
      const testPdf2 = path.join(__dirname, 'fixtures', 'resume2.pdf');

      const response = await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Senior Software Engineer')
        .field('skills', 'JavaScript, React, Node.js')
        .field('education', 'Bachelor degree')
        .field('experience', '5 years')
        .attach('resumes', testPdf1)
        .attach('resumes', testPdf2)
        .expect(200);

      expect(response.body).toBeInstanceOf(Array);
      expect(response.body.length).toBe(2);

      // Verify results are sorted by total score (descending)
      if (response.body.length > 1) {
        expect(response.body[0].ts).toBeGreaterThanOrEqual(response.body[1].ts);
      }
    });

    it.skip('should reject invalid file types', async () => {
      const testFilePath = path.join(__dirname, 'fixtures', 'malicious.exe');

      await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Test')
        .field('skills', 'Test')
        .field('education', 'Test')
        .field('experience', '1 year')
        .attach('resumes', testFilePath)
        .expect(400);
    });

    it.skip('should require all job requirement fields', async () => {
      const testPdfPath = path.join(__dirname, 'fixtures', 'test-resume.pdf');

      // Missing skills field
      await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Test')
        .field('education', 'Test')
        .field('experience', '1 year')
        .attach('resumes', testPdfPath)
        .expect(400);
    });

    it.skip('should require at least one resume file', async () => {
      await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Test')
        .field('skills', 'Test')
        .field('education', 'Test')
        .field('experience', '1 year')
        .expect(400);
    });

    it.skip('should handle Python API errors gracefully', async () => {
      // This test would require mocking Python API to return errors
      // or temporarily stopping the Python API service

      const testPdfPath = path.join(__dirname, 'fixtures', 'test-resume.pdf');

      const response = await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Test')
        .field('skills', 'Test')
        .field('education', 'Test')
        .field('experience', '1 year')
        .attach('resumes', testPdfPath);

      // Should return 500 or appropriate error code
      expect([500, 503]).toContain(response.status);
      expect(response.body).toHaveProperty('error');
    });
  });

  describe('Health Check Endpoint', () => {
    it.skip('should return healthy status', async () => {
      const response = await request(app)
        .get('/health')
        .expect('Content-Type', /json/)
        .expect(200);

      expect(response.body).toHaveProperty('status');
      expect(response.body.status).toBe('healthy');
    });
  });

  describe('Error Handling', () => {
    it.skip('should handle file size limit exceeded', async () => {
      // Create a large file that exceeds the 10MB limit
      const largePdfPath = path.join(__dirname, 'fixtures', 'large-resume.pdf');

      await request(app)
        .post('/resume-screening')
        .field('jobDescription', 'Test')
        .field('skills', 'Test')
        .field('education', 'Test')
        .field('experience', '1 year')
        .attach('resumes', largePdfPath)
        .expect(413); // Payload too large
    });

    it.skip('should handle too many files', async () => {
      const testPdfPath = path.join(__dirname, 'fixtures', 'test-resume.pdf');
      const request = require('supertest')(app)
        .post('/resume-screening')
        .field('jobDescription', 'Test')
        .field('skills', 'Test')
        .field('education', 'Test')
        .field('experience', '1 year');

      // Attach more files than maxFiles limit (default 10)
      for (let i = 0; i < 11; i++) {
        request.attach('resumes', testPdfPath);
      }

      await request.expect(400);
    });
  });
});

/**
 * Integration Test Setup Guide:
 *
 * 1. Create test fixtures directory:
 *    mkdir -p tests/integration/fixtures
 *
 * 2. Add sample PDF files to fixtures:
 *    - test-resume.pdf
 *    - resume1.pdf
 *    - resume2.pdf
 *
 * 3. Ensure Python API is running:
 *    cd python-api && python app.py
 *
 * 4. Run integration tests:
 *    npm test -- tests/integration/
 *
 * 5. To enable tests, remove .skip from test cases
 */
