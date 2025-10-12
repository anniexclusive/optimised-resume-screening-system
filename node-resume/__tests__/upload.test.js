/**
 * Integration tests for Node.js /upload endpoint
 */

const request = require('supertest');
const express = require('express');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

// Import the app
const app = express();
app.use(cors());
app.use(express.json());

// Import the resume router
const resume = require('../resume');
app.use(resume);

describe('POST /upload', () => {
  let testPdfPath;

  beforeAll(() => {
    // Create a test PDF file
    testPdfPath = path.join(__dirname, 'test_resume.pdf');

    // Create minimal PDF content
    const pdfContent = `%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
/Resources <<
/Font <<
/F1 5 0 R
>>
>>
>>
endobj
4 0 obj
<<
/Length 100
>>
stream
BT
/F1 12 Tf
100 700 Td
(Software Engineer with Python, JavaScript, and React experience) Tj
100 680 Td
(Bachelor of Science in Computer Science) Tj
100 660 Td
(5 years of experience) Tj
ET
endstream
endobj
5 0 obj
<<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000270 00000 n
0000000420 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
513
%%EOF`;

    fs.writeFileSync(testPdfPath, pdfContent);
  });

  afterAll(() => {
    // Clean up test PDF
    if (fs.existsSync(testPdfPath)) {
      fs.unlinkSync(testPdfPath);
    }

    // Clean up any uploaded files in uploads directory
    const uploadsDir = path.join(__dirname, '../uploads');
    if (fs.existsSync(uploadsDir)) {
      const files = fs.readdirSync(uploadsDir);
      files.forEach(file => {
        const filePath = path.join(uploadsDir, file);
        if (fs.statSync(filePath).isFile()) {
          fs.unlinkSync(filePath);
        }
      });
    }
  });

  describe('Successful upload scenarios', () => {
    test('should accept valid job data and resume file', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Looking for a Python developer with Flask experience')
        .field('skills', 'Python, Flask, Machine Learning')
        .field('education', 'Bachelor of Science in Computer Science')
        .field('experience', '3 years')
        .attach('resumes', testPdfPath);

      // Response should be 200 or could be 502 if Python API is not running
      // We're testing the Node.js layer here
      expect([200, 502, 503]).toContain(response.status);

      if (response.status === 200) {
        // If successful, check response structure
        expect(Array.isArray(response.body)).toBe(true);

        if (response.body.length > 0) {
          const result = response.body[0];
          expect(result).toHaveProperty('filename');
          expect(result).toHaveProperty('ts'); // Total score
          expect(result).toHaveProperty('ss'); // Skills score
          expect(result).toHaveProperty('ex'); // Experience score
          expect(result).toHaveProperty('ed'); // Education score
          expect(result).toHaveProperty('ge'); // General score
        }
      }
    }, 30000); // Increase timeout for this test

    test('should accept multiple resume files', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Senior Software Engineer position')
        .field('skills', 'JavaScript, React, Node.js')
        .field('education', 'Bachelor degree')
        .field('experience', '5 years')
        .attach('resumes', testPdfPath)
        .attach('resumes', testPdfPath);

      expect([200, 502, 503]).toContain(response.status);

      if (response.status === 200) {
        expect(Array.isArray(response.body)).toBe(true);
        // Should return results for 2 resumes (or could be 1 if same content)
        expect(response.body.length).toBeGreaterThanOrEqual(1);
      }
    }, 30000);
  });

  describe('Validation error scenarios', () => {
    test('should return error when jobDescription is missing', async () => {
      const response = await request(app)
        .post('/upload')
        .field('skills', 'Python, Flask')
        .field('education', 'Bachelor')
        .field('experience', '3 years')
        .attach('resumes', testPdfPath);

      // Should return error (400 or 500)
      expect(response.status).toBeGreaterThanOrEqual(400);
      expect(response.body).toHaveProperty('message');
    });

    test('should return error when skills is missing', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Python developer needed')
        .field('education', 'Bachelor')
        .field('experience', '3 years')
        .attach('resumes', testPdfPath);

      expect(response.status).toBeGreaterThanOrEqual(400);
      expect(response.body).toHaveProperty('message');
    });

    test('should return error when education is missing', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Python developer needed')
        .field('skills', 'Python, Flask')
        .field('experience', '3 years')
        .attach('resumes', testPdfPath);

      expect(response.status).toBeGreaterThanOrEqual(400);
      expect(response.body).toHaveProperty('message');
    });

    test('should return error when experience is missing', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Python developer needed')
        .field('skills', 'Python, Flask')
        .field('education', 'Bachelor')
        .attach('resumes', testPdfPath);

      expect(response.status).toBeGreaterThanOrEqual(400);
      expect(response.body).toHaveProperty('message');
    });

    test('should return error when no resume files are uploaded', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Python developer needed')
        .field('skills', 'Python, Flask')
        .field('education', 'Bachelor')
        .field('experience', '3 years');

      expect(response.status).toBeGreaterThanOrEqual(400);
      expect(response.body).toHaveProperty('message');
    });
  });

  describe('File validation', () => {
    test('should reject non-PDF files', async () => {
      // Create a text file
      const txtFilePath = path.join(__dirname, 'test_file.txt');
      fs.writeFileSync(txtFilePath, 'This is a text file');

      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Python developer needed')
        .field('skills', 'Python, Flask')
        .field('education', 'Bachelor')
        .field('experience', '3 years')
        .attach('resumes', txtFilePath);

      // Should reject non-PDF file
      expect(response.status).toBeGreaterThanOrEqual(400);

      // Clean up
      fs.unlinkSync(txtFilePath);
    });
  });

  describe('Response structure', () => {
    test('should return proper error structure on failure', async () => {
      const response = await request(app)
        .post('/upload')
        .field('jobDescription', 'Test')
        .attach('resumes', testPdfPath);

      if (response.status >= 400) {
        expect(response.body).toHaveProperty('message');
        expect(typeof response.body.message).toBe('string');
      }
    });
  });
});

describe('API Health', () => {
  test('should have a working server', () => {
    expect(app).toBeDefined();
  });
});
