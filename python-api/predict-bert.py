from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from flask import Flask, request, jsonify, json
from skill_edu import education_keywords, skill_dataset, degree_equivalents

app = Flask(__name__)

# Download stopwords if not already downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))

# Load pre-trained BERT model for embeddings
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF resume (given a PDF file object) and cleans it."""
    if isinstance(pdf_file, str):  # If the input is a file path, open the file
        with open(pdf_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
            text = text.lower()  # Convert to lowercase
    else:  # If the input is already a file object
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
        text = text.lower()  # Convert to lowercase
    return text 

def clean_text(text):
    # Check if the text is valid and non-empty
    if pd.isna(text) or text.strip() == "":
        return ""  # or return some default text
    """Cleans the extracted text by removing special characters, numbers, and stopwords."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)  # Remove special characters
    text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
    return text

def remove_sensitive_info(text):
    """Removes potential bias-related words from resume text."""
    bias_keywords = ["male", "female", "black", "white", "asian", "african", "hispanic", "married", "single"]
    for word in bias_keywords:
        text = text.replace(word, " ")
    return text

def filter_skills(applicant_skills, job_skills):
    """Extract job matchings skills from applicant skills."""
    if isinstance(job_skills, str):
        job_skills = [item.strip() for item in job_skills.split(", ")]
    skills = {skill for skill in applicant_skills if skill in job_skills}
    return skills

def extract_entities(text):
    """Efficiently extracts skills, education, and experience from resume text."""
    extracted_info = {"skills": set(), "education": set(), "experience": set()} 
    
    experience_patterns = [
        r'(\d+\s*[+-]?\s*(?:years?|yrs?))',
    ]

    text = text.lower()
    skill_data = {skill.lower() for skill in skill_dataset}  
    education_data = {edu.lower() for edu in education_keywords}

    # Extract experience using regex
    for pattern in experience_patterns:
        for match in re.findall(pattern, text):
            extracted_info["experience"].add("-".join(match) if isinstance(match, tuple) else match)

    text = clean_text(text)

    # Fast set-based matching for skills and education
    extracted_info["skills"] = {skill for skill in skill_data if skill in text}
    extracted_info["education"] = {edu for edu in education_data if edu in text}

    return extracted_info 


def extract_experience(text):
    """Extracts the numerical years of experience from text."""
    match = re.findall(r'(\d+)\s*(?:\+|-)?\s*years?', text)
    if match:
        return max(map(int, match))  # Take the highest number found
    return 0  # Default if no experience is mentioned

def compute_experience_score(resume_exp, job_exp, similarity_score):
    """Computes the final experience score combining numerical experience and text similarity."""
    resume_years = extract_experience(resume_exp)
    job_years = extract_experience(job_exp)

    if job_years == 0:  # No required experience specified
        num_experience_score = 1.0  # Full score if no experience requirement
    else:
        num_experience_score = min(resume_years / job_years, 1.5)  # Cap scaling at 1.5 to avoid over-rewarding

    # Multiply structured experience score with text similarity score to balance both
    final_experience_score = num_experience_score * similarity_score  

    return final_experience_score

def qualification_similarity(resume_qualification, job_qualification):
    """Boosts similarity for predefined degree equivalents."""
    score = compute_similarity(resume_qualification, job_qualification)  # Original BERT score

    # Check if any equivalent degree exists in the mappings
    for degree in resume_qualification.split(", "):
        for key, equivalents in degree_equivalents.items():
            if degree in equivalents and key in job_qualification:
                score += 0.5  # Small boost for recognized equivalent degrees
    
    return min(score, 1.0)  # Ensure the score doesn’t exceed 1.0

def compute_similarity(text1, text2):
    """Compute cosine similarity between two text embeddings."""
    embedding1 = bert_model.encode(text1).reshape(1, -1)
    embedding2 = bert_model.encode(text2).reshape(1, -1)
    return cosine_similarity(embedding1, embedding2)[0][0]

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
    if scores["ge"] > 5:
        explanation.append("GS: aligns well.")
    else:
        explanation.append("GS: does not strongly align .")

    return " ".join(explanation)


# def get_resume_ranking_score(resume_text, job_description):
#     """Ranks resumes using BERT embeddings and cosine similarity."""
#     # Extract and clean resume text
#     cleaned_resume = remove_sensitive_info(clean_text(resume_text)) # remove bias

#     # Encode the resume and job description
#     resume_embedding = bert_model.encode(cleaned_resume)
#     job_embedding = bert_model.encode(job_description)

#     # Compute similarity score
#     similarity_score = cosine_similarity([resume_embedding], [job_embedding])[0][0]
    
#     return float(similarity_score)


@app.route('/predictbert', methods=['POST'])
def predictbert():
    job_data = {
        "description": request.form['job_description'],
        "skills": request.form['skills'],
        "experience": request.form['experience'],
        "education": request.form['education']
    }
    
    files = request.files.getlist("resumes")
    ranked_resumes = []
    # predefined_skills = set(required_skills)
    
    for file in files:
        filename = file.filename

        resume_text = extract_text_from_pdf(file)
        
        # similarity_score = get_resume_ranking_score(resume_text, job_data['description'])
        ranking_data = extract_entities(resume_text)
        ranking_data['r_skills'] = filter_skills(ranking_data['skills'], job_data['skills'])
        ranking_data = {key: ", ".join(value) for key, value in ranking_data.items()}
        ranking_data["resume_text"] = remove_sensitive_info(clean_text(resume_text)) # remove bias
        ranking_data["filename"] = filename

        scores = get_resume_ranking_score(ranking_data, job_data)
        ranking_data["explanation"] = generate_explanation(scores, job_data)
        # Drop the key 'resume_text'
        del ranking_data['resume_text']
        result = ranking_data | scores

        ranked_resumes.append(result)

    ranked_resumes.sort(key=lambda x: x["ts"], reverse=True)

    return jsonify(ranked_resumes)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
