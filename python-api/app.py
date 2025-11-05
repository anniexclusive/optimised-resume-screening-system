"""
Resume Screening API
Main Flask application with comprehensive error handling and security
"""
from flask import Flask, request, jsonify
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge
import logging
from typing import Dict, Any
import os

from utils.pdf_processing import extract_text_from_pdf
from utils.text_processing import clean_text, remove_sensitive_info
from utils.extraction import extract_entities, filter_skills
from utils.scoring import get_resume_ranking_score, generate_explanation
from config.model_config import FLASK_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security configurations
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max request size
app.config['JSON_SORT_KEYS'] = False

# Constants
MAX_FILES = int(os.getenv('MAX_FILES', 10))
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB per file
ALLOWED_EXTENSIONS = {'pdf'}


def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_job_data(form_data) -> Dict[str, str]:
    """
    Validate and extract job data from request form.

    Args:
        form_data: Flask request.form object

    Returns:
        Dictionary with validated job data

    Raises:
        BadRequest: If required fields are missing or invalid
    """
    required_fields = ['job_description', 'skills', 'experience', 'education']

    for field in required_fields:
        if field not in form_data or not form_data[field].strip():
            raise BadRequest(f"Missing or empty required field: {field}")

    # Validate field lengths
    if len(form_data['job_description']) > 10000:
        raise BadRequest("Job description too long (max 10000 characters)")

    if len(form_data['skills']) > 5000:
        raise BadRequest("Skills list too long (max 5000 characters)")

    if len(form_data['experience']) > 2000:
        raise BadRequest("Experience description too long (max 2000 characters)")

    if len(form_data['education']) > 2000:
        raise BadRequest("Education description too long (max 2000 characters)")

    return {
        "description": form_data['job_description'].strip(),
        "skills": form_data['skills'].strip(),
        "experience": form_data['experience'].strip(),
        "education": form_data['education'].strip()
    }


def validate_files(files) -> None:
    """
    Validate uploaded files.

    Args:
        files: List of uploaded files

    Raises:
        BadRequest: If files are invalid
    """
    if not files or len(files) == 0:
        raise BadRequest("No resume files provided")

    if len(files) > MAX_FILES:
        raise BadRequest(f"Too many files (max {MAX_FILES})")

    for file in files:
        if not file.filename:
            raise BadRequest("File has no filename")

        if not allowed_file(file.filename):
            raise BadRequest(f"Invalid file type for {file.filename}. Only PDF files allowed")

        # Check file size (if available)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)  # Reset file pointer

        if file_length > MAX_FILE_SIZE:
            raise BadRequest(f"File {file.filename} too large (max {MAX_FILE_SIZE // (1024*1024)}MB)")


def process_single_resume(file, job_data: Dict[str, str]) -> Dict[str, Any]:
    """
    Process a single resume file.

    Args:
        file: Uploaded file object
        job_data: Dictionary containing job requirements

    Returns:
        Dictionary with resume ranking data

    Raises:
        Exception: If processing fails
    """
    try:
        # Extract text from PDF
        resume_text = extract_text_from_pdf(file)

        if not resume_text or len(resume_text.strip()) < 50:
            raise ValueError(f"Resume {file.filename} contains insufficient text")

        # Extract entities
        ranking_data = extract_entities(resume_text)
        ranking_data['r_skills'] = filter_skills(ranking_data['skills'], job_data['skills'])
        ranking_data["resume_text"] = remove_sensitive_info(clean_text(resume_text))

        # Convert sets to strings for JSON serialization
        ranking_data = {
            k: ", ".join(v) if isinstance(v, (set, tuple)) else v
            for k, v in ranking_data.items()
        }
        ranking_data["filename"] = file.filename

        # Calculate scores
        scores = get_resume_ranking_score(ranking_data, job_data)
        ranking_data["explanation"] = generate_explanation(scores, job_data)

        # Remove resume text from response
        del ranking_data['resume_text']

        # Combine data and scores
        result = ranking_data | scores

        logger.info(f"Successfully processed resume: {file.filename}")
        return result

    except Exception as e:
        logger.error(f"Error processing resume {file.filename}: {str(e)}")
        raise


@app.errorhandler(400)
def bad_request_error(error):
    """Handle bad request errors."""
    logger.warning(f"Bad request: {str(error)}")
    return jsonify({
        "error": "Bad Request",
        "message": str(error.description) if hasattr(error, 'description') else str(error)
    }), 400


@app.errorhandler(413)
def request_too_large_error(error):
    """Handle request entity too large errors."""
    logger.warning("Request entity too large")
    return jsonify({
        "error": "Request Too Large",
        "message": "Request size exceeds maximum allowed size"
    }), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500


@app.errorhandler(Exception)
def handle_unexpected_error(error):
    """Handle any unexpected errors."""
    logger.error(f"Unexpected error: {str(error)}", exc_info=True)
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Liveness probe - Check if service is alive (basic health).

    Returns:
        200: Service process is running
    """
    return jsonify({
        "status": "healthy",
        "service": "resume-screening-api",
        "version": "1.0.0"
    }), 200


@app.route('/ready', methods=['GET'])
def readiness_check():
    """
    Readiness probe - Check if service is ready to accept traffic.
    Verifies BERT model is loaded and ready for predictions.

    Returns:
        - 200: Service is ready (model loaded)
        - 503: Service is not ready (model loading or error)
    """
    health_status = {
        "status": "ready",
        "service": "resume-screening-api",
        "version": "1.0.0"
    }

    try:
        # Check if BERT model is loaded and ready
        from utils.similarity import get_calculator
        calculator = get_calculator()

        # Verify model is actually loaded (not just lazy-loaded)
        model_loaded = calculator._model is not None

        health_status["model_loaded"] = model_loaded
        health_status["model_name"] = calculator.model_name if hasattr(calculator, 'model_name') else "unknown"

        if not model_loaded:
            health_status["status"] = "not_ready"
            health_status["message"] = "BERT model not loaded yet (lazy loading enabled)"
            return jsonify(health_status), 503

        return jsonify(health_status), 200

    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        health_status["status"] = "not_ready"
        health_status["model_loaded"] = False
        health_status["error"] = str(e)
        return jsonify(health_status), 503


@app.route('/predictbert', methods=['POST'])
def predictbert():
    """
    Process resumes and rank them against job requirements.

    Expected form data:
        - job_description: Job description text
        - skills: Required skills (comma-separated)
        - experience: Required experience description
        - education: Required education description
        - resumes: Multiple PDF files

    Returns:
        JSON array of ranked resumes with scores
    """
    try:
        logger.info("Received resume screening request")

        # Validate job data
        job_data = validate_job_data(request.form)

        # Validate files
        files = request.files.getlist("resumes")
        validate_files(files)

        logger.info(f"Processing {len(files)} resume(s)")

        # Process resumes
        ranked_resumes = []
        errors = []

        for file in files:
            try:
                result = process_single_resume(file, job_data)
                ranked_resumes.append(result)
            except Exception as e:
                error_msg = f"Failed to process {file.filename}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        # Sort by total score (descending)
        ranked_resumes.sort(key=lambda x: x.get("ts", 0), reverse=True)

        response = {
            "success": True,
            "total_processed": len(ranked_resumes),
            "total_failed": len(errors),
            "results": ranked_resumes
        }

        if errors:
            response["errors"] = errors

        logger.info(f"Successfully processed {len(ranked_resumes)}/{len(files)} resumes")

        return jsonify(response), 200

    except BadRequest:
        raise  # Let error handler handle it
    except RequestEntityTooLarge:
        raise  # Let error handler handle it
    except Exception as e:
        logger.error(f"Unexpected error in predictbert: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    logger.info("Starting Resume Screening API")
    logger.info(f"Configuration: host={FLASK_CONFIG['host']}, port={FLASK_CONFIG['port']}, debug={FLASK_CONFIG['debug']}")

    app.run(
        host=FLASK_CONFIG['host'],
        port=FLASK_CONFIG['port'],
        debug=FLASK_CONFIG['debug']
    )
