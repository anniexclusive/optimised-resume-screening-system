"""
Integration tests for Python API endpoints
"""

import pytest
import io
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_pdf_file():
    """Create a mock PDF file for testing with sufficient content"""
    # Create a realistic PDF with enough text content (>50 chars minimum)
    # This simulates a real resume with skills, experience, and education
    pdf_content = b"""%PDF-1.4
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
/Length 450
>>
stream
BT
/F1 16 Tf
100 750 Td
(John Doe - Software Engineer) Tj
0 -30 Td
/F1 12 Tf
(Email: john.doe@example.com | Phone: 555-1234) Tj
0 -30 Td
(PROFESSIONAL SUMMARY) Tj
0 -20 Td
/F1 10 Tf
(Experienced Python developer with 5 years of software development experience.) Tj
0 -15 Td
(Strong expertise in Flask, Django, Machine Learning, and cloud technologies.) Tj
0 -15 Td
(Bachelor of Science in Computer Science from State University.) Tj
0 -30 Td
/F1 12 Tf
(TECHNICAL SKILLS) Tj
0 -20 Td
/F1 10 Tf
(Languages: Python, JavaScript, SQL) Tj
0 -15 Td
(Frameworks: Flask, Django, React) Tj
0 -15 Td
(Tools: Docker, Kubernetes, AWS, Git) Tj
0 -15 Td
(Machine Learning: TensorFlow, PyTorch, scikit-learn) Tj
0 -30 Td
/F1 12 Tf
(WORK EXPERIENCE) Tj
0 -20 Td
/F1 10 Tf
(Senior Python Developer at Tech Corp \\(2020-Present\\)) Tj
0 -15 Td
(- Developed ML-powered applications using Flask and PyTorch) Tj
0 -15 Td
(- Implemented RESTful APIs serving 1M+ requests per day) Tj
0 -15 Td
(- Led migration to microservices architecture using Docker) Tj
0 -30 Td
(Python Developer at StartupXYZ \\(2018-2020\\)) Tj
0 -15 Td
(- Built data processing pipelines with Pandas and NumPy) Tj
0 -15 Td
(- Created automated testing frameworks using pytest) Tj
0 -30 Td
/F1 12 Tf
(EDUCATION) Tj
0 -20 Td
/F1 10 Tf
(Bachelor of Science in Computer Science) Tj
0 -15 Td
(State University, 2018, GPA: 3.8/4.0) Tj
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
0000000769 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
857
%%EOF"""

    return (io.BytesIO(pdf_content), 'test_resume.pdf')


@pytest.fixture
def valid_job_data():
    """Valid job requirements data"""
    return {
        'job_description': 'Looking for a Python developer with Flask experience',
        'skills': 'Python, Flask, Machine Learning',
        'education': 'Bachelor of Science in Computer Science',
        'experience': '3 years'
    }


class TestHealthEndpoint:
    """Test cases for health check endpoint"""

    def test_health_check(self, client):
        """Test health endpoint returns 200"""
        response = client.get('/health')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'healthy'


class TestPredictBertEndpoint:
    """Test cases for /predictbert endpoint"""

    def test_predictbert_success(self, client, sample_pdf_file, valid_job_data):
        """Test successful resume screening"""
        pdf_file, filename = sample_pdf_file

        data = {
            'job_description': valid_job_data['job_description'],
            'skills': valid_job_data['skills'],
            'education': valid_job_data['education'],
            'experience': valid_job_data['experience'],
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 200
        result = response.get_json()

        # Check response structure
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'results' in result
        assert result['success'] is True
        assert isinstance(result['results'], list)
        assert len(result['results']) > 0

        # Check first resume result
        resume_result = result['results'][0]
        assert 'filename' in resume_result
        assert 'ts' in resume_result  # Total score
        assert 'ss' in resume_result  # Skills score
        assert 'ex' in resume_result  # Experience score
        assert 'ed' in resume_result  # Education score
        assert 'ge' in resume_result  # General score
        assert 'explanation' in resume_result

        # Verify score types
        assert isinstance(resume_result['ts'], (int, float))
        assert isinstance(resume_result['ss'], (int, float))
        assert isinstance(resume_result['ex'], (int, float))
        assert isinstance(resume_result['ed'], (int, float))
        assert isinstance(resume_result['ge'], (int, float))

    def test_predictbert_missing_job_description(self, client, sample_pdf_file):
        """Test with missing job_description field"""
        pdf_file, filename = sample_pdf_file

        data = {
            'skills': 'Python, Flask',
            'education': 'Bachelor',
            'experience': '3 years',
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        # Should fail with 400 or 500
        assert response.status_code in [400, 500]

    def test_predictbert_missing_skills(self, client, sample_pdf_file):
        """Test with missing skills field"""
        pdf_file, filename = sample_pdf_file

        data = {
            'job_description': 'Python developer needed',
            'education': 'Bachelor',
            'experience': '3 years',
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        # Should fail with 400 or 500
        assert response.status_code in [400, 500]

    def test_predictbert_missing_education(self, client, sample_pdf_file):
        """Test with missing education field"""
        pdf_file, filename = sample_pdf_file

        data = {
            'job_description': 'Python developer needed',
            'skills': 'Python, Flask',
            'experience': '3 years',
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        # Should fail with 400 or 500
        assert response.status_code in [400, 500]

    def test_predictbert_missing_experience(self, client, sample_pdf_file):
        """Test with missing experience field"""
        pdf_file, filename = sample_pdf_file

        data = {
            'job_description': 'Python developer needed',
            'skills': 'Python, Flask',
            'education': 'Bachelor',
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        # Should fail with 400 or 500
        assert response.status_code in [400, 500]

    def test_predictbert_no_resumes(self, client, valid_job_data):
        """Test with no resume files"""
        data = {
            'job_description': valid_job_data['job_description'],
            'skills': valid_job_data['skills'],
            'education': valid_job_data['education'],
            'experience': valid_job_data['experience']
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        # Should fail with 400 or 500
        assert response.status_code in [400, 500]

    def test_predictbert_multiple_resumes(self, client, sample_pdf_file, valid_job_data):
        """Test with multiple resume files"""
        pdf_file1, filename1 = sample_pdf_file

        # Create second PDF
        pdf_content2 = pdf_file1.getvalue()
        pdf_file2 = io.BytesIO(pdf_content2)
        filename2 = 'test_resume_2.pdf'

        data = {
            'job_description': valid_job_data['job_description'],
            'skills': valid_job_data['skills'],
            'education': valid_job_data['education'],
            'experience': valid_job_data['experience'],
            'resumes': [
                (pdf_file1, filename1),
                (pdf_file2, filename2)
            ]
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code == 200
        result = response.get_json()

        # Should return results for 2 resumes
        assert isinstance(result, dict)
        assert result['success'] is True
        assert isinstance(result['results'], list)
        assert len(result['results']) == 2

    def test_predictbert_results_sorted_by_score(self, client, sample_pdf_file, valid_job_data):
        """Test that results are sorted by total score descending"""
        pdf_file1, filename1 = sample_pdf_file

        # Create second PDF
        pdf_content2 = pdf_file1.getvalue()
        pdf_file2 = io.BytesIO(pdf_content2)
        filename2 = 'test_resume_2.pdf'

        data = {
            'job_description': valid_job_data['job_description'],
            'skills': valid_job_data['skills'],
            'education': valid_job_data['education'],
            'experience': valid_job_data['experience'],
            'resumes': [
                (pdf_file1, filename1),
                (pdf_file2, filename2)
            ]
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        result = response.get_json()

        # Verify results are sorted by ts (total score) descending
        assert isinstance(result, dict)
        assert result['success'] is True
        results_list = result['results']
        if len(results_list) > 1:
            for i in range(len(results_list) - 1):
                assert results_list[i]['ts'] >= results_list[i + 1]['ts']


class TestScoring:
    """Test cases for scoring logic"""

    def test_score_components_sum_correctly(self, client, sample_pdf_file, valid_job_data):
        """Test that component scores are within expected ranges"""
        pdf_file, filename = sample_pdf_file

        data = {
            'job_description': valid_job_data['job_description'],
            'skills': valid_job_data['skills'],
            'education': valid_job_data['education'],
            'experience': valid_job_data['experience'],
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        json_response = response.get_json()
        assert isinstance(json_response, dict)
        assert json_response['success'] is True
        assert len(json_response['results']) > 0

        result = json_response['results'][0]

        # Each component should be >= 0
        assert result['ss'] >= 0  # Skills score
        assert result['ex'] >= 0  # Experience score
        assert result['ed'] >= 0  # Education score
        assert result['ge'] >= 0  # General score

        # Total score should be approximately sum of components
        # (allowing for rounding differences)
        calculated_total = result['ss'] + result['ex'] + result['ed'] + result['ge']
        assert abs(result['ts'] - calculated_total) < 0.1

    def test_explanation_field_not_empty(self, client, sample_pdf_file, valid_job_data):
        """Test that explanation field is populated"""
        pdf_file, filename = sample_pdf_file

        data = {
            'job_description': valid_job_data['job_description'],
            'skills': valid_job_data['skills'],
            'education': valid_job_data['education'],
            'experience': valid_job_data['experience'],
            'resumes': (pdf_file, filename)
        }

        response = client.post(
            '/predictbert',
            data=data,
            content_type='multipart/form-data'
        )

        json_response = response.get_json()
        assert isinstance(json_response, dict)
        assert json_response['success'] is True
        assert len(json_response['results']) > 0

        result = json_response['results'][0]

        # Explanation should exist and not be empty
        assert 'explanation' in result
        assert isinstance(result['explanation'], str)
        assert len(result['explanation']) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
