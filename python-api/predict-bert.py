from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np
import PyPDF2
import re
import nltk
from nltk.corpus import stopwords
from flask import Flask, request, jsonify, json
from skill_edu import education_keywords, skill_dataset

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
    else:  # If the input is already a file object (PdfFileReader accepts file-like objects)
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

    return text 

def clean_text(text):
    # Check if the text is valid and non-empty
    if pd.isna(text) or text.strip() == "":
        return ""  # or return some default text
    """Cleans the extracted text by removing special characters, numbers, and stopwords."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters
    text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
    return text

def to_lower(text_array):
    if text_array:
        lowercase_array = list(map(str.lower, text_array))
        return lowercase_array
    else:
        return []

def remove_sensitive_info(text):
    """Removes potential bias-related words from resume text."""
    bias_keywords = ["male", "female", "black", "white", "asian", "hispanic", "married", "single"]
    for word in bias_keywords:
        text = text.replace(word, " ")
    return text

def extract_entities(text):
    """Efficiently extracts skills, education, and experience from resume text."""
    extracted_info = {"Skills": set(), "Education": set(), "Experience": set()}
    # Regex patterns to capture different ways experience is written
    experience_patterns = [
        r'(\d+)\s*(?:\+|-)?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',  # e.g., "5 years of experience"
        r'(\d+)\s*(?:\+|-)?\s*(?:years?|yrs?)\s*(?:in|working in|as)',  # e.g., "3+ years in software development"
        r'(\d+)-(\d+)\s*years'  # e.g., "3-5 years experience"
    ]

    # Convert text to lowercase for case-insensitive matching
    text = text.lower()
    skill_data = to_lower(skill_dataset)
    education_data = to_lower(education_keywords)

    # Regex-based experience extraction
    # Extract matches using regex
    for pattern in experience_patterns:
        matches = re.findall(pattern, text)
        if matches:
            for match in matches:
                if isinstance(match, tuple):  # Handles cases like "3-5 years"
                    extracted_info["Experience"].add(f"{match[0]}-{match[1]} years")
                else:
                    extracted_info["Experience"].add(f"{match} years")

    text = clean_text(text)

    # Fast skill matching using set intersection
    extracted_info["Skills"] = {skill for skill in skill_data if skill in text}

    # Fast education matching
    extracted_info["Education"] = {edu for edu in education_data if edu in text}

    return {
        "skills": list(extracted_info["Skills"]),
        "education": list(extracted_info["Education"]),
        "experience": list(extracted_info["Experience"])
    }

def get_resume_ranking_score(resume_text, job_description):
    """Ranks resumes using BERT embeddings and cosine similarity."""
    # Extract and clean resume text
    cleaned_resume = remove_sensitive_info(clean_text(resume_text)) # remove bias

    # Encode the resume and job description
    resume_embedding = bert_model.encode(cleaned_resume)
    job_embedding = bert_model.encode(job_description)

    # Compute similarity score
    similarity_score = cosine_similarity([resume_embedding], [job_embedding])[0][0]
    
    return float(similarity_score)


@app.route('/predictbert', methods=['POST'])
def predictbert():
    job_desc = request.form['job_description']
    skills_json = request.form.get('skills')
    required_skills = json.loads(skills_json)  # Deserialize the JSON string
    files = request.files.getlist("resumes")
    ranked_resumes = []
    predefined_skills = set(required_skills)
    
    for file in files:
        filename = file.filename

        resume_text = extract_text_from_pdf(file)
        job_description = clean_text(job_desc)
        
        similarity_score = get_resume_ranking_score(resume_text, job_description)
        ranking_data = extract_entities(resume_text)
        ranking_data["filename"] = filename
        ranking_data["score"] = round(similarity_score, 2)

        ranked_resumes.append(ranking_data)

    ranked_resumes.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(ranked_resumes)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)

