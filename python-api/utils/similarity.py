"""
Similarity utilities
"""

from utils.skill_edu import degree_equivalents
from services.similarityService import BERTSimilarityCalculator
from config.scoring_config import DEGREE_EQUIVALENTS_BOOST


# Singleton instance to avoid reloading BERT model
_similarity_calculator = None


def get_calculator():
    """Get or create the similarity calculator instance"""
    global _similarity_calculator
    if _similarity_calculator is None:
        _similarity_calculator = BERTSimilarityCalculator()
    return _similarity_calculator


def qualification_similarity(resume_qualification, job_qualification):
    """
    Boosts similarity for predefined degree equivalents.

    Args:
        resume_qualification: Resume education/qualification text
        job_qualification: Job requirement education/qualification text

    Returns:
        float: Similarity score between 0 and 1
    """
    calculator = get_calculator()
    score = calculator.compute_similarity(resume_qualification, job_qualification)

    # Check if any equivalent degree exists in the mappings
    for degree in resume_qualification.split(", "):
        for key, equivalents in degree_equivalents.items():
            if degree in equivalents and key in job_qualification:
                score += DEGREE_EQUIVALENTS_BOOST  # Boost from config

    return min(score, 1.0)  # Ensure the score doesn't exceed 1.0


def compute_similarity(text1, text2):
    """
    Compute cosine similarity between two text embeddings.

    Args:
        text1: First text
        text2: Second text

    Returns:
        float: Similarity score between 0 and 1
    """
    calculator = get_calculator()
    return calculator.compute_similarity(text1, text2)
