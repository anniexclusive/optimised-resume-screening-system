const axios = require("axios");
const FormData = require("form-data");
const fs = require("fs");
const path = require("path");
const express = require('express')
const multer = require("multer");

const router = express.Router();
const PYTHON_API_URL = "http://localhost:8000/predictbert"; // Change to your Python API URL



// Configure Multer for file storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    if (!fs.existsSync("uploads")) {
      fs.mkdirSync("uploads");
    }
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    cb(null, `${Date.now()}-${file.originalname}`);
  },
});

const upload = multer({ storage });
const form = new FormData();

// Route for handling file upload & forwarding to Python API
router.post("/upload", upload.array("resumes"), async (req, res) => {
    const form = new FormData();
    
    try {
        console.log("in upload");

        const fileNames = req.files.map((file) => file.path);

        // Convert skills string into an array
        const skillsArray = req.body.skills.split(',').map(skill => skill.trim());
        fileNames.forEach(file => {
            form.append("resumes", fs.createReadStream(file));
        });

        // Append job details
        form.append("skills", JSON.stringify(skillsArray));
        form.append("job_description", req.body.jobDescription);
    
        // Send data to Python API
        const pythonResponse = await axios.post(PYTHON_API_URL, form, {
            headers: form.getHeaders(),
        });
      
      // Return Python API response to frontend
      res.json(pythonResponse.data);
  
    } catch (error) {
      console.error("Error:", error.message);
      res.status(500).json({ message: "Server Error", error: error.message });
    }
});

async function screenResumes(pdfPaths, skills, jobDescription) {
    const form = new FormData();
    pdfPaths.forEach(file => {
        form.append("resumes", fs.createReadStream(file));
    });

    // Append job details
    form.append("skills", JSON.stringify(skills));
    form.append("job_description", jobDescription);

    try {
        const response = await axios.post(PYTHON_API_URL, form, {
            headers: form.getHeaders(),
        });
        console.log("Screening Results:", response.data);
    } catch (error) {
        console.error("Error calling AI model:", error.message);
    }
}

module.exports = router;
// Example usage
//const pdfFiles = ["data-scientist-1.pdf"];
// Define the folder where your PDFs are stored
// const pdfFolder = "../ai-resume-screening/applicants_resumes"; // Change this to your actual folder path

// // Read all PDF files from the directory
// const pdfFiles = fs.readdirSync(pdfFolder)
//     .filter(file => file.endsWith(".pdf")) // Only select PDF files
//     .map(file => path.join(pdfFolder, file)); // Get full path

// const jobDescription = "Our client is looking for a PHP Symfony Developer who impresses with Practical  experience in the backend development of websites and applications as well as with APIs. Good knowledge of PHP (Symfony) and MySQL as well as object-oriented programming and an understanding of database and caching systems such as MySQL, Redis and ElasticSearch are an advantage. experience in software design techniques, test-driven development and distributed architecture. excellent communication skills. Fluent written and spoken German or English";
// const skills = ["symfony", "php", "mysql", "APIs", "frontend developer", "backend"]
// screenResumes(pdfFiles, skills, jobDescription);
