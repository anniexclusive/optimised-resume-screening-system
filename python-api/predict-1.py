from flask import Flask, request, jsonify
import fitz
import pandas as pd
import numpy as np
import re
import string
import os
import fitz  # PyMuPDF for PDF text extraction
import spacy  # NLP library for text processing
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.neighbors import NearestNeighbors
import joblib

app = Flask(__name__)

# Load models===========================================================================================================
model = joblib.load(open('resume_screening_model.pkl', 'rb'))
vectorizer = joblib.load(open('tfidf_vectorizer.pkl', 'rb'))

# Clean resume==========================================================================================================
def cleanResume(txt):
    cleanText = re.sub(r'http\S+\s', ' ', txt)
    cleanText = re.sub(r'RT|cc', ' ', cleanText)
    cleanText = re.sub(r'#\S+\s', ' ', cleanText)
    cleanText = re.sub(r'@\S+', '  ', cleanText)
    cleanText = re.sub(r'[%s]' % re.escape(r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', cleanText)
    cleanText = re.sub(r'[^\x00-\x7f]', ' ', cleanText)
    cleanText = re.sub(r'\s+', ' ', cleanText)
    return cleanText

# Extract text from a PDF file (in-memory)
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = " ".join([page.get_text("text") for page in doc])
    return nlp_preprocess(text)


# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Advanced text preprocessing using spaCy
def nlp_preprocess(text):
    if isinstance(text, str):
        cleaned_text = cleanResume(text)
        doc = nlp(cleaned_text.lower())  # Convert to lowercase and process text
        tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
        return " ".join(tokens)
    return ""

# Extract relevant skills and qualifications from resume
def extract_resume_info(text):
    cleaned_text = cleanResume(text)
    doc = nlp(cleaned_text)
    # skills = [ent.text for ent in doc.ents if ent.label_ in ["SKILLS", "EDUCATION", "DEGREE"]]
    skills = {ent.label_: ent.text for ent in doc.ents}
    # return ", ".join(set(skills))  # Remove duplicates
    return skills

# Combine job title and job description for ranking
def combine_title_description(job_title, job_description):
    return clean_text(job_title) + " " + clean_text(job_description)

# Resume ranking based on job title and description
# def rank_resumes(job_title, job_description, resume_texts, top_n=5):
#     if not resume_texts:
#         return []  # No resumes uploaded
#     job_text_combined = combine_title_description(job_title, job_description)
#     job_vector = vectorizer.transform([job_text_combined])
    
#     # Predict job category using the trained model
#     predicted_category = model.predict(job_vector)[0]
    
#      # Use Nearest Neighbors to find similar resumes among applicants
#     if not df_applicants.empty:
#         X_applicants = vectorizer.transform(df_applicants['cleaned_resume'])
#         nn = NearestNeighbors(n_neighbors=min(top_n, len(df_applicants)), metric='cosine')
#         nn.fit(X_applicants)
#         distances, indices = nn.kneighbors(job_vector)
        
#         # Add ranking scores
#         ranked_resumes = df_applicants.iloc[indices[0]].copy()
#         ranked_resumes['score'] = 1 - distances[0]  # Convert cosine distance to similarity score
#         ranked_resumes['predicted_category'] = predicted_category  # Add predicted category
#         return ranked_resumes.sort_values(by='score', ascending=False)
#     else:
#         return pd.DataFrame()  # Return empty DataFrame if no resumes are found

# Rank resumes based on job title and description
def rank_resumes(resume_texts, job_title, job_description, top_n=5):
    if df_applicants.empty:
        return []  # No resumes uploaded

    # Convert job details into a vector
    job_text_combined = combine_title_description(job_title, job_description)
    job_vector = vectorizer.transform([job_text_combined])

    # Predict job category
    predicted_category = model.predict(job_vector)[0]

    # Convert resumes into a vectorized format
    resume_vectors = vectorizer.transform(resume_texts)

    # Use Nearest Neighbors to rank resumes
    nn = NearestNeighbors(n_neighbors=min(top_n, len(resume_texts)), metric='cosine')
    nn.fit(resume_vectors)
    distances, indices = nn.kneighbors(job_vector)

    # Create a ranking list
    ranked_resumes = []
    for i, idx in enumerate(indices[0]):
        ranked_resumes.append({
            "filename": df_applicants.iloc[idx]["filename"],
            "score": round(1 - distances[0][i], 2),  # Convert cosine distance to similarity score
            "predicted_category": predicted_category
        })

    return ranked_resumes
    
@app.route('/predict_old', methods=['POST'])
def predict():
    job_title = request.form['job_title']
    job_desc = request.form['job_description']
    files = request.files.getlist("resumes")
    
    job_text_combined = nlp_preprocess(job_title + " " + job_desc)
    job_vector = vectorizer.transform([job_text_combined])
    
    # Predict job category
    predicted_category = model.predict(job_vector)[0]
    
    ranked_resumes = []
    
    for file in files:
        filename = file.filename
        resume_text = extract_text_from_pdf(file)
        skills = extract_resume_info(resume_text)

        # Convert resume text to vector and compare similarity
        resume_vector = vectorizer.transform([resume_text])
        similarity_score = 1 - NearestNeighbors(n_neighbors=1, metric='cosine').fit(resume_vector).kneighbors(job_vector)[0][0][0]

        ranked_resumes.append({
            "filename": filename,
            "skills": skills,
            "score": round(similarity_score, 2),
            "predicted_category": predicted_category
        })

    ranked_resumes.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(ranked_resumes)
        
    # results = {
    #     "job_title": job_title,
    #     "job_description": job_description,
    #     "candidates": {}
    # }
    # df_applicant = []

    # for file in files:
    #     pdf_path = f"temp_{file.filename}"
    #     file.save(pdf_path)
    #     df_applicant["resume_text"] = extract_text_from_pdf(pdf_path)
    #     top_resumes = rank_resumes(job_title, job_desc, resume_text, top_n=5)
    #     skills = extract_resume_info(resume_text) or "none"
    #     results["candidates"][file.filename] = {"score": 85, "category": "Software Engineer", "skills": skills}  # Replace with model logic

    # return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
