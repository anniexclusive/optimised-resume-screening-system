"""
Pytest configuration and fixtures
Shared fixtures for all tests
"""
import pytest
import os
from services.similarityService import BERTSimilarityCalculator, MockSimilarityCalculator


@pytest.fixture(scope="session")
def bert_model():
    """
    Session-scoped fixture to load BERT model once for all tests.
    Saves ~2-3 minutes by not reloading the model for every test.
    """
    # Set environment to use mock calculator for faster tests
    # Override in specific tests that need real BERT
    os.environ['USE_MOCK_SIMILARITY'] = 'false'

    # Load model once
    calculator = BERTSimilarityCalculator()

    yield calculator


@pytest.fixture(scope="function")
def mock_similarity():
    """
    Function-scoped fixture for tests that don't need real BERT.
    Use this for unit tests to speed them up significantly.
    """
    calculator = MockSimilarityCalculator()

    yield calculator


@pytest.fixture
def sample_job_data():
    """Sample job data for testing"""
    return {
        'description': 'Python developer with ML experience',
        'skills': 'Python, Machine Learning, Flask',
        'education': 'Bachelor of Science in Computer Science',
        'experience': '3 years'
    }


@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing"""
    return {
        'resume_text': 'Experienced Python developer with 3 years in ML',
        'r_skills': 'Python, TensorFlow, Flask, Docker',
        'education': 'BS Computer Science',
        'experience': 3
    }
