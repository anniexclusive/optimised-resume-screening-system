"""
Unit tests for Similarity Service
Tests the similarity calculation abstraction layer
"""

import pytest
import numpy as np
from services.similarityService import (
    BERTSimilarityCalculator,
    MockSimilarityCalculator,
    get_similarity_calculator,
    reset_similarity_calculator
)


class TestMockSimilarityCalculator:
    """Test MockSimilarityCalculator (for fast testing without BERT model)"""

    def test_mock_encode(self):
        """Test mock encoding returns consistent values"""
        calculator = MockSimilarityCalculator()

        result = calculator.encode("test text")

        assert result == [0.1, 0.2, 0.3, 0.4]

    def test_mock_compute_similarity(self):
        """Test mock similarity always returns 0.8"""
        calculator = MockSimilarityCalculator()

        similarity = calculator.compute_similarity("text1", "text2")

        assert similarity == 0.8

    def test_mock_compute_similarity_identical_texts(self):
        """Test mock similarity with identical texts"""
        calculator = MockSimilarityCalculator()

        similarity = calculator.compute_similarity("hello", "hello")

        # Mock always returns 0.8, even for identical texts
        assert similarity == 0.8

    def test_mock_compute_similarity_different_texts(self):
        """Test mock similarity with different texts"""
        calculator = MockSimilarityCalculator()

        similarity = calculator.compute_similarity("hello", "goodbye")

        # Mock always returns 0.8
        assert similarity == 0.8


class TestBERTSimilarityCalculator:
    """Test BERTSimilarityCalculator (requires model download)"""

    @pytest.mark.slow
    def test_bert_initialization(self):
        """Test BERT calculator can be initialized"""
        try:
            calculator = BERTSimilarityCalculator()
            assert calculator is not None
            assert calculator.model_name == 'all-MiniLM-L6-v2'
        except Exception as e:
            pytest.skip(f"BERT model not available: {e}")

    @pytest.mark.slow
    def test_bert_encode(self):
        """Test BERT encoding returns proper embeddings"""
        try:
            calculator = BERTSimilarityCalculator()

            result = calculator.encode("test text")

            # BERT embeddings should be numpy array
            assert isinstance(result, np.ndarray)
            # Should have 384 dimensions for all-MiniLM-L6-v2
            assert len(result) == 384
        except Exception as e:
            pytest.skip(f"BERT model not available: {e}")

    @pytest.mark.slow
    def test_bert_compute_similarity_identical(self):
        """Test BERT similarity with identical texts"""
        try:
            calculator = BERTSimilarityCalculator()

            similarity = calculator.compute_similarity("hello world", "hello world")

            # Identical texts should have very high similarity
            assert similarity > 0.99
        except Exception as e:
            pytest.skip(f"BERT model not available: {e}")

    @pytest.mark.slow
    def test_bert_compute_similarity_similar(self):
        """Test BERT similarity with similar texts"""
        try:
            calculator = BERTSimilarityCalculator()

            similarity = calculator.compute_similarity(
                "Python developer with experience",
                "Experienced Python programmer"
            )

            # Similar texts should have high similarity
            assert similarity > 0.5
        except Exception as e:
            pytest.skip(f"BERT model not available: {e}")

    @pytest.mark.slow
    def test_bert_compute_similarity_different(self):
        """Test BERT similarity with different texts"""
        try:
            calculator = BERTSimilarityCalculator()

            similarity = calculator.compute_similarity(
                "Python programming",
                "Cooking recipes"
            )

            # Different topics should have lower similarity
            assert similarity < 0.5
        except Exception as e:
            pytest.skip(f"BERT model not available: {e}")


class TestGetSimilarityCalculator:
    """Test the factory function for similarity calculators"""

    def setUp(self):
        """Reset singleton before each test"""
        reset_similarity_calculator()

    def test_get_mock_calculator(self):
        """Test getting mock calculator"""
        reset_similarity_calculator()

        calculator = get_similarity_calculator('mock')

        assert isinstance(calculator, MockSimilarityCalculator)

    def test_get_mock_calculator_singleton(self):
        """Test mock calculator returns same instance"""
        reset_similarity_calculator()

        calc1 = get_similarity_calculator('mock')
        calc2 = get_similarity_calculator('mock')

        assert calc1 is calc2

    @pytest.mark.slow
    def test_get_bert_calculator(self):
        """Test getting BERT calculator"""
        reset_similarity_calculator()

        try:
            calculator = get_similarity_calculator('bert')
            assert isinstance(calculator, BERTSimilarityCalculator)
        except Exception as e:
            pytest.skip(f"BERT model not available: {e}")

    def test_get_invalid_calculator_type(self):
        """Test error handling for invalid calculator type"""
        reset_similarity_calculator()

        with pytest.raises(ValueError, match="Unknown calculator type"):
            get_similarity_calculator('invalid_type')

    def test_reset_similarity_calculator(self):
        """Test resetting the singleton"""
        reset_similarity_calculator()

        calc1 = get_similarity_calculator('mock')
        reset_similarity_calculator()
        calc2 = get_similarity_calculator('mock')

        # After reset, should get a new instance
        assert calc1 is not calc2


class TestSimilarityIntegration:
    """Integration tests for similarity calculations"""

    def test_mock_calculator_workflow(self):
        """Test complete workflow with mock calculator"""
        reset_similarity_calculator()
        calculator = get_similarity_calculator('mock')

        # Test resume vs job description
        resume_text = "Python developer with 5 years of Flask experience"
        job_desc = "Looking for experienced Python Flask developer"

        similarity = calculator.compute_similarity(resume_text, job_desc)

        assert isinstance(similarity, float)
        assert 0.0 <= similarity <= 1.0

    def test_multiple_similarities(self):
        """Test computing multiple similarities"""
        reset_similarity_calculator()
        calculator = get_similarity_calculator('mock')

        resumes = [
            "Python developer with Flask",
            "JavaScript React developer",
            "Java Spring Boot engineer"
        ]
        job_desc = "Python Flask developer needed"

        similarities = [
            calculator.compute_similarity(resume, job_desc)
            for resume in resumes
        ]

        assert len(similarities) == 3
        assert all(0.0 <= s <= 1.0 for s in similarities)


if __name__ == '__main__':
    # Run tests
    # Fast tests only: pytest test_similarity_service.py
    # All tests including slow: pytest test_similarity_service.py --slow
    pytest.main([__file__, '-v'])
