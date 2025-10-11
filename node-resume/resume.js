/**
 * Resume Routes
 * Refactored to use service layer (SOLID principles)
 */

const express = require('express');
const { fileService, resumeService } = require('./services');

const router = express.Router();

// Get upload middleware from file service
const upload = fileService.getUploadMiddleware();

/**
 * POST /upload
 * Handle resume upload and screening
 */
router.post("/upload", upload.array("resumes"), async (req, res) => {
    try {
        console.log("[Route] Received upload request");

        // Extract job data from request
        const jobData = {
            jobDescription: req.body.jobDescription,
            skills: req.body.skills,
            education: req.body.education,
            experience: req.body.experience
        };

        // Process resumes using resume service
        const results = await resumeService.screenResumes(jobData, req.files);

        // Optional: Clean up files after processing
        // await resumeService.cleanupFiles(req.files);

        // Return results
        res.json(results);

    } catch (error) {
        console.error("[Route] Error:", error.message);

        // Handle errors appropriately
        const statusCode = error.status || 500;
        res.status(statusCode).json({
            message: error.message || "Server Error",
            details: error.details || null
        });
    }
});

module.exports = router;
