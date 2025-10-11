"""
Scoring utilities using configuration
"""

from utils.similarity import compute_similarity, qualification_similarity
from utils.extraction import extract_experience
from config.scoring_config import SCORING_WEIGHTS, THRESHOLDS, EXPERIENCE_CONFIG


def get_resume_ranking_score(ranking_data, job_data):
    """
    Provides a detailed breakdown of resume scoring.

    Args:
        ranking_data: Dictionary containing resume information
        job_data: Dictionary containing job requirements

    Returns:
        dict: Breakdown of scores (ts, ss, ex, ed, ge)
    """
    # Compute similarity scores for different sections using weights from config
    general_score = (
        compute_similarity(ranking_data["resume_text"], job_data["description"])
        * SCORING_WEIGHTS['general'] * 100
    )

    skills_score = (
        compute_similarity(ranking_data["r_skills"], job_data["skills"])
        * SCORING_WEIGHTS['skills'] * 100
    )

    experience_similarity = compute_similarity(
        ranking_data["resume_text"],
        job_data["experience"]
    )
    experience_score = (
        compute_experience_score(
            ranking_data["experience"],
            job_data["experience"],
            experience_similarity
        ) * SCORING_WEIGHTS['experience'] * 100
    )

    education_score = (
        qualification_similarity(ranking_data["education"], job_data["education"])
        * SCORING_WEIGHTS['education'] * 100
    )

    # Calculate total score
    total_score = skills_score + experience_score + education_score + general_score

    # Return breakdown
    return {
        "ts": round(total_score, 2),
        "ss": round(skills_score, 2),
        "ex": round(experience_score, 2),
        "ed": round(education_score, 2),
        "ge": round(general_score, 2)
    }


def compute_experience_score(resume_years, job_exp, similarity_score):
    """
    Computes the final experience score combining numerical experience and text similarity.

    Args:
        resume_years: Years of experience from resume
        job_exp: Job experience requirement
        similarity_score: Text similarity score

    Returns:
        float: Final experience score
    """
    job_years = extract_experience(job_exp)

    if job_years == 0:  # No required experience specified
        num_experience_score = EXPERIENCE_CONFIG['no_requirement_score']
    else:
        # Use max scaling factor from config
        num_experience_score = min(
            resume_years / job_years,
            EXPERIENCE_CONFIG['max_scaling_factor']
        )

    # Multiply structured experience score with text similarity score to balance both
    final_experience_score = num_experience_score * similarity_score

    return final_experience_score


def generate_explanation(scores, job_requirements=None):
    """
    Generates a human-readable explanation based on the breakdown of resume scores.

    Args:
        scores: Dictionary of score breakdown
        job_requirements: Optional job requirements (not used currently)

    Returns:
        str: Human-readable explanation
    """
    explanation = []

    # Skills Explanation
    if scores["ss"] > THRESHOLDS['skills']['strong']:
        explanation.append("SS: strong skill.")
    else:
        explanation.append("SS: lacks some required skills.")

    # Experience Explanation
    if scores["ex"] > THRESHOLDS['experience']['strong']:
        explanation.append("EX: relevant work experience.")
    else:
        explanation.append("EX: less experience.")

    # Education Explanation
    if scores["ed"] > THRESHOLDS['education']['strong']:
        explanation.append("ED: meets the required qualifications.")
    else:
        explanation.append("ED: does not fully meet the qualifications.")

    # General Matching Explanation
    if scores["ge"] > THRESHOLDS['general']['strong']:
        explanation.append("GS: aligns well.")
    else:
        explanation.append("GS: does not strongly align.")

    return " ".join(explanation)
