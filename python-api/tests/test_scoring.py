"""
Unit tests for Scoring utilities
Tests configuration-driven scoring logic
"""

import unittest
from unittest.mock import patch
from utils.scoring import get_resume_ranking_score, compute_experience_score, generate_explanation
from config.scoring_config import SCORING_WEIGHTS, THRESHOLDS, EXPERIENCE_CONFIG


class TestGetResumeRankingScore(unittest.TestCase):
    """Test resume ranking score calculation"""

    @patch('utils.scoring.compute_similarity')
    @patch('utils.scoring.qualification_similarity')
    def test_score_calculation_with_config_weights(self, mock_qual_sim, mock_compute_sim):
        """Test that scoring uses weights from configuration"""
        # Mock similarity functions to return fixed values
        mock_compute_sim.return_value = 0.8
        mock_qual_sim.return_value = 0.9

        ranking_data = {
            "resume_text": "Python developer",
            "r_skills": "Python, Flask",
            "experience": 3,  # Numeric value (years)
            "education": "BS Computer Science"
        }
        
        job_data = {
            "description": "Python developer needed",
            "skills": "Python, Flask",
            "experience": "3 years",
            "education": "BS"
        }

        scores = get_resume_ranking_score(ranking_data, job_data)

        # Verify all score components are present
        self.assertIn('ts', scores)
        self.assertIn('ss', scores)
        self.assertIn('ex', scores)
        self.assertIn('ed', scores)
        self.assertIn('ge', scores)

        # Verify scores are numbers
        self.assertIsInstance(scores['ts'], (int, float))
        self.assertIsInstance(scores['ss'], (int, float))

    @patch('utils.scoring.compute_similarity')
    @patch('utils.scoring.qualification_similarity')
    def test_score_weights_sum_correctly(self, mock_qual_sim, mock_compute_sim):
        """Test that individual scores sum to total score"""
        mock_compute_sim.return_value = 0.5
        mock_qual_sim.return_value = 0.5

        ranking_data = {
            "resume_text": "Test",
            "r_skills": "Test",
            "experience": 2,  # Numeric value
            "education": "Test"
        }
        
        job_data = {
            "description": "Test",
            "skills": "Test",
            "experience": "2 years",
            "education": "Test"
        }

        scores = get_resume_ranking_score(ranking_data, job_data)

        # Calculate expected sum (with small tolerance for rounding)
        component_sum = scores['ss'] + scores['ex'] + scores['ed'] + scores['ge']
        self.assertAlmostEqual(scores['ts'], component_sum, places=1)


class TestComputeExperienceScore(unittest.TestCase):
    """Test experience score computation"""

    @patch('utils.scoring.extract_experience')
    def test_no_experience_required(self, mock_extract):
        """Test scoring when no experience is required"""
        mock_extract.return_value = 0

        score = compute_experience_score(5, "No experience needed", 0.8)

        # Should return no_requirement_score * similarity
        expected = EXPERIENCE_CONFIG['no_requirement_score'] * 0.8
        self.assertAlmostEqual(score, expected, places=2)

    @patch('utils.scoring.extract_experience')
    def test_exact_experience_match(self, mock_extract):
        """Test scoring when experience exactly matches"""
        mock_extract.return_value = 3

        score = compute_experience_score(3, "3 years", 0.9)

        # Should return (3/3) * 0.9 = 0.9
        self.assertAlmostEqual(score, 0.9, places=2)

    @patch('utils.scoring.extract_experience')
    def test_experience_exceeds_requirement(self, mock_extract):
        """Test max scaling factor is applied"""
        mock_extract.return_value = 3

        score = compute_experience_score(10, "3 years", 1.0)

        # Should be capped at max_scaling_factor * 1.0
        expected = EXPERIENCE_CONFIG['max_scaling_factor'] * 1.0
        self.assertAlmostEqual(score, expected, places=2)

    @patch('utils.scoring.extract_experience')
    def test_insufficient_experience(self, mock_extract):
        """Test scoring when resume has less experience than required"""
        mock_extract.return_value = 5

        score = compute_experience_score(2, "5 years", 0.7)

        # Should return (2/5) * 0.7 = 0.28
        expected = (2 / 5) * 0.7
        self.assertAlmostEqual(score, expected, places=2)


class TestGenerateExplanation(unittest.TestCase):
    """Test explanation generation"""

    def test_strong_candidate_explanation(self):
        """Test explanation for strong candidate"""
        scores = {
            "ss": 35,  # Above strong threshold (30)
            "ex": 25,  # Above strong threshold (20)
            "ed": 15,  # Above strong threshold (12)
            "ge": 8,   # Above strong threshold (7)
            "ts": 83
        }

        explanation = generate_explanation(scores)

        # Should contain positive indicators
        self.assertIn("strong skill", explanation)
        self.assertIn("relevant work experience", explanation)
        self.assertIn("meets the required qualifications", explanation)
        self.assertIn("aligns well", explanation)

    def test_weak_candidate_explanation(self):
        """Test explanation for weak candidate"""
        scores = {
            "ss": 15,  # Below strong threshold
            "ex": 10,  # Below strong threshold
            "ed": 8,   # Below strong threshold
            "ge": 4,   # Below strong threshold
            "ts": 37
        }

        explanation = generate_explanation(scores)

        # Should contain negative indicators
        self.assertIn("lacks some required skills", explanation)
        self.assertIn("less experience", explanation)
        self.assertIn("does not fully meet the qualifications", explanation)
        self.assertIn("does not strongly align", explanation)

    def test_mixed_candidate_explanation(self):
        """Test explanation for candidate with mixed scores"""
        scores = {
            "ss": 32,  # Strong
            "ex": 15,  # Weak
            "ed": 14,  # Strong
            "ge": 5,   # Weak
            "ts": 66
        }

        explanation = generate_explanation(scores)

        # Should have mix of positive and negative
        self.assertIn("strong skill", explanation)
        self.assertIn("less experience", explanation)
        self.assertIn("meets the required qualifications", explanation)
        self.assertIn("does not strongly align", explanation)


class TestConfigurationIntegration(unittest.TestCase):
    """Test that configuration values are used correctly"""

    def test_scoring_weights_are_used(self):
        """Verify SCORING_WEIGHTS from config are applied"""
        # This test ensures weights are loaded
        self.assertEqual(sum(SCORING_WEIGHTS.values()), 1.0)
        self.assertIn('general', SCORING_WEIGHTS)
        self.assertIn('skills', SCORING_WEIGHTS)
        self.assertIn('experience', SCORING_WEIGHTS)
        self.assertIn('education', SCORING_WEIGHTS)

    def test_thresholds_are_defined(self):
        """Verify THRESHOLDS from config exist"""
        self.assertIn('skills', THRESHOLDS)
        self.assertIn('experience', THRESHOLDS)
        self.assertIn('education', THRESHOLDS)
        self.assertIn('general', THRESHOLDS)

        # Check strong thresholds exist
        self.assertIn('strong', THRESHOLDS['skills'])
        self.assertIn('strong', THRESHOLDS['experience'])

    def test_experience_config_exists(self):
        """Verify EXPERIENCE_CONFIG is loaded"""
        self.assertIn('max_scaling_factor', EXPERIENCE_CONFIG)
        self.assertIn('no_requirement_score', EXPERIENCE_CONFIG)
        self.assertIsInstance(EXPERIENCE_CONFIG['max_scaling_factor'], (int, float))


if __name__ == '__main__':
    unittest.main()
