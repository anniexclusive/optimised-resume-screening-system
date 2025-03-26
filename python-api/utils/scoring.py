from utils.similarity import compute_similarity, qualification_similarity
from utils.extraction import extract_experience

def get_resume_ranking_score(ranking_data, job_data):
    """Provides a detailed breakdown of resume scoring."""
    
    # Compute similarity scores for different sections
    general_score = compute_similarity(ranking_data["resume_text"], job_data["description"]) * 10  # 10% weight
    skills_score = compute_similarity(ranking_data["r_skills"], job_data["skills"]) * 40  # 40% weight
    experience_similarity = compute_similarity(ranking_data["resume_text"], job_data["experience"])  
    experience_score = compute_experience_score(ranking_data["experience"], job_data["experience"], experience_similarity) * 30  # 30% weight
    education_score = qualification_similarity(ranking_data["education"], job_data["education"]) * 20  # 20% weight
    
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
    """Computes the final experience score combining numerical experience and text similarity."""
    job_years = extract_experience(job_exp)

    if job_years == 0:  # No required experience specified
        num_experience_score = 1.0  # Full score if no experience requirement
    else:
        num_experience_score = min(resume_years / job_years, 1.5)  # Cap scaling at 1.5 to avoid over-rewarding

    # Multiply structured experience score with text similarity score to balance both
    final_experience_score = num_experience_score * similarity_score  

    return final_experience_score

def generate_explanation(scores, job_requirements):
    """
    Generates a human-readable explanation based on the breakdown of resume scores.
    """
    explanation = []

    # Skills Explanation
    if scores["ss"] > 30:  
        explanation.append("SS: strong skill.")
    else:
        explanation.append("SS: lacks some required skills.")

    # Experience Explanation
    if scores["ex"] > 20:
        explanation.append("EX: relevant work experience.")
    else:
        explanation.append("EX: less experience.")

    # Education Explanation
    if scores["ed"] > 12:
        explanation.append("ED: meets the required qualifications.")
    else:
        explanation.append("ED: does not fully meet the qualifications.")

    # General Matching Explanation
    if scores["ge"] > 7:
        explanation.append("GS: aligns well.")
    else:
        explanation.append("GS: does not strongly align .")

    return " ".join(explanation)
