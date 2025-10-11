"""
Scoring Configuration
Centralized configuration for resume scoring weights and thresholds
"""

import os

# Scoring Weights (must sum to 100)
SCORING_WEIGHTS = {
    'general': float(os.getenv('WEIGHT_GENERAL', 0.10)),      # 10% weight
    'skills': float(os.getenv('WEIGHT_SKILLS', 0.40)),        # 40% weight
    'experience': float(os.getenv('WEIGHT_EXPERIENCE', 0.30)), # 30% weight
    'education': float(os.getenv('WEIGHT_EDUCATION', 0.20))   # 20% weight
}

# Thresholds for scoring explanations
THRESHOLDS = {
    'skills': {
        'strong': 30,
        'description': 'Strong skills match'
    },
    'experience': {
        'strong': 20,
        'description': 'Relevant work experience'
    },
    'education': {
        'strong': 12,
        'description': 'Meets required qualifications'
    },
    'general': {
        'strong': 7,
        'description': 'Aligns well with job description'
    }
}

# Experience Scoring Configuration
EXPERIENCE_CONFIG = {
    'max_scaling_factor': float(os.getenv('EXP_MAX_SCALING', 1.5)),  # Cap at 1.5x
    'no_requirement_score': 1.0  # Full score if no experience required
}

# Degree equivalents boost score
DEGREE_EQUIVALENTS_BOOST = float(os.getenv('DEGREE_BOOST', 0.5))

def validate_weights():
    """Validate that scoring weights sum to 1.0"""
    total = sum(SCORING_WEIGHTS.values())
    if abs(total - 1.0) > 0.01:  # Allow small floating point errors
        raise ValueError(f"Scoring weights must sum to 1.0, got {total}")

# Validate on module load
validate_weights()
