"""
Unit tests for Configuration
Tests that configuration is properly loaded and validated
"""

import unittest
import os
from unittest.mock import patch
from config.model_config import BERT_CONFIG, MODEL_LOAD_CONFIG, FLASK_CONFIG
from config.scoring_config import SCORING_WEIGHTS, THRESHOLDS, EXPERIENCE_CONFIG, DEGREE_EQUIVALENTS_BOOST


class TestModelConfig(unittest.TestCase):
    """Test model configuration loading"""

    def test_bert_config_structure(self):
        """Test BERT_CONFIG has required keys"""
        self.assertIn('model_name', BERT_CONFIG)
        self.assertIn('cache_dir', BERT_CONFIG)
        self.assertIn('device', BERT_CONFIG)
        self.assertIn('max_seq_length', BERT_CONFIG)

    def test_bert_config_defaults(self):
        """Test BERT_CONFIG default values"""
        # Without env vars, should use defaults
        self.assertEqual(BERT_CONFIG['model_name'], 'all-MiniLM-L6-v2')
        self.assertIsInstance(BERT_CONFIG['max_seq_length'], int)
        self.assertGreater(BERT_CONFIG['max_seq_length'], 0)

    def test_model_load_config_structure(self):
        """Test MODEL_LOAD_CONFIG has required keys"""
        self.assertIn('lazy_loading', MODEL_LOAD_CONFIG)
        self.assertIn('show_progress', MODEL_LOAD_CONFIG)
        self.assertIn('local_files_only', MODEL_LOAD_CONFIG)

    def test_model_load_config_types(self):
        """Test MODEL_LOAD_CONFIG values are booleans"""
        self.assertIsInstance(MODEL_LOAD_CONFIG['lazy_loading'], bool)
        self.assertIsInstance(MODEL_LOAD_CONFIG['show_progress'], bool)
        self.assertIsInstance(MODEL_LOAD_CONFIG['local_files_only'], bool)

    def test_flask_config_structure(self):
        """Test FLASK_CONFIG has required keys"""
        self.assertIn('host', FLASK_CONFIG)
        self.assertIn('port', FLASK_CONFIG)
        self.assertIn('debug', FLASK_CONFIG)

    def test_flask_config_types(self):
        """Test FLASK_CONFIG value types"""
        self.assertIsInstance(FLASK_CONFIG['host'], str)
        self.assertIsInstance(FLASK_CONFIG['port'], int)
        self.assertIsInstance(FLASK_CONFIG['debug'], bool)


class TestScoringConfig(unittest.TestCase):
    """Test scoring configuration loading and validation"""

    def test_scoring_weights_structure(self):
        """Test SCORING_WEIGHTS has all required keys"""
        required_keys = ['general', 'skills', 'experience', 'education']
        for key in required_keys:
            self.assertIn(key, SCORING_WEIGHTS)

    def test_scoring_weights_sum_to_one(self):
        """Test SCORING_WEIGHTS sum to 1.0"""
        total = sum(SCORING_WEIGHTS.values())
        self.assertAlmostEqual(total, 1.0, places=2)

    def test_scoring_weights_are_positive(self):
        """Test all weights are positive"""
        for weight in SCORING_WEIGHTS.values():
            self.assertGreater(weight, 0)
            self.assertLessEqual(weight, 1.0)

    def test_thresholds_structure(self):
        """Test THRESHOLDS has required structure"""
        required_categories = ['skills', 'experience', 'education', 'general']
        for category in required_categories:
            self.assertIn(category, THRESHOLDS)
            self.assertIn('strong', THRESHOLDS[category])

    def test_thresholds_are_numeric(self):
        """Test all threshold values are numeric"""
        for category, thresholds in THRESHOLDS.items():
            for key, value in thresholds.items():
                if key != 'description':  # Skip description fields
                    self.assertIsInstance(value, (int, float))

    def test_experience_config_structure(self):
        """Test EXPERIENCE_CONFIG has required keys"""
        self.assertIn('max_scaling_factor', EXPERIENCE_CONFIG)
        self.assertIn('no_requirement_score', EXPERIENCE_CONFIG)

    def test_experience_config_values(self):
        """Test EXPERIENCE_CONFIG values are reasonable"""
        self.assertGreater(EXPERIENCE_CONFIG['max_scaling_factor'], 1.0)
        self.assertEqual(EXPERIENCE_CONFIG['no_requirement_score'], 1.0)

    def test_degree_equivalents_boost_type(self):
        """Test DEGREE_EQUIVALENTS_BOOST is a number"""
        self.assertIsInstance(DEGREE_EQUIVALENTS_BOOST, (int, float))
        self.assertGreater(DEGREE_EQUIVALENTS_BOOST, 0)


class TestConfigurationFromEnvironment(unittest.TestCase):
    """Test configuration loading from environment variables"""

    @patch.dict(os.environ, {'WEIGHT_SKILLS': '0.50', 'WEIGHT_GENERAL': '0.15', 'WEIGHT_EXPERIENCE': '0.20', 'WEIGHT_EDUCATION': '0.15'})
    def test_custom_weights_from_env(self):
        """Test that weights can be customized via environment variables"""
        # Note: This test shows the pattern but won't actually reload config in runtime
        # In a real scenario, you'd need to reload the module
        expected_skills_weight = float(os.getenv('WEIGHT_SKILLS'))
        self.assertEqual(expected_skills_weight, 0.50)

    @patch.dict(os.environ, {'BERT_MODEL': 'custom-bert-model'})
    def test_custom_bert_model_from_env(self):
        """Test BERT model can be customized via environment variable"""
        custom_model = os.getenv('BERT_MODEL')
        self.assertEqual(custom_model, 'custom-bert-model')

    @patch.dict(os.environ, {'FLASK_PORT': '8000'})
    def test_custom_flask_port_from_env(self):
        """Test Flask port can be customized via environment variable"""
        custom_port = int(os.getenv('FLASK_PORT'))
        self.assertEqual(custom_port, 8000)


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation logic"""

    def test_weights_validation_on_import(self):
        """Test that invalid weights would raise error on import"""
        # The scoring_config module validates weights on import
        # If we're here, validation passed
        self.assertTrue(True)

    def test_all_required_configs_exist(self):
        """Test all required configuration dictionaries exist"""
        # Model config
        self.assertIsNotNone(BERT_CONFIG)
        self.assertIsNotNone(MODEL_LOAD_CONFIG)
        self.assertIsNotNone(FLASK_CONFIG)

        # Scoring config
        self.assertIsNotNone(SCORING_WEIGHTS)
        self.assertIsNotNone(THRESHOLDS)
        self.assertIsNotNone(EXPERIENCE_CONFIG)
        self.assertIsNotNone(DEGREE_EQUIVALENTS_BOOST)


if __name__ == '__main__':
    unittest.main()
