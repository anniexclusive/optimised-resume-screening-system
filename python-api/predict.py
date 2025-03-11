from flask import Flask, request, jsonify, json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import PyPDF2
import spacy  # NLP library for text processing
import re
from nltk.corpus import stopwords
import nltk
from difflib import get_close_matches

app = Flask(__name__)

# Download stopwords if not already downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))
# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_file):
    """Extracts text from a PDF resume (given a PDF file object) and cleans it."""
    if isinstance(pdf_file, str):  # If the input is a file path, open the file
        with open(pdf_file, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    else:  # If the input is already a file object (PdfFileReader accepts file-like objects)
        reader = PyPDF2.PdfReader(pdf_file)
        text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])

    return clean_text(text)

def clean_text(text):
    # Check if the text is valid and non-empty
    if pd.isna(text) or text.strip() == "":
        return ""  # or return some default text
    """Cleans the extracted text by removing special characters, numbers, and stopwords."""
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special characters and numbers
    text = " ".join([word for word in text.split() if word not in stop_words])  # Remove stopwords
    return text

# Extract relevant skills and qualifications from resume
def extract_resume_info(text):
    doc = nlp(cleaned_text)
    skills = [ent.text for ent in doc.ents if ent.label_ in ["SKILLS", "EDUCATION", "DEGREE"]]
    # skills = {ent.label_: ent.text for ent in doc.ents}
    return ", ".join(set(skills))  # Remove duplicates
    # return skills

def rank_real_resume(resume_text, job_description, vectorizer):
    """Ranks a real resume against job descriptions using TF-IDF."""
    tfidf_resume = vectorizer.transform([resume_text])
    tfidf_job = vectorizer.transform([job_description])
    similarity_score = cosine_similarity(tfidf_resume, tfidf_job)[0][0]
    return similarity_score

# def extract_relevant_skills(resume_text, job_description, vectorizer):
#     """Extracts relevant skills from the resume based on the job description using TF-IDF."""
#     tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
#     feature_names = vectorizer.get_feature_names_out()
    
#     # Get TF-IDF scores for resume and job description
#     resume_tfidf_scores = tfidf_matrix.toarray()[0]
#     job_tfidf_scores = tfidf_matrix.toarray()[1]
    
#     # Identify words in resume that are also in job description with high TF-IDF scores
#     relevant_skills = [feature_names[i] for i in range(len(feature_names)) if resume_tfidf_scores[i] > 0 and job_tfidf_scores[i] > 0]
    
#     return relevant_skills

def extract_relevant_skills(resume_text, predefined_skills):
    """Extracts predefined relevant skills from the resume text."""
    words = set(resume_text.split())  # Convert resume text into a set of words
    matched_skills = words.intersection(predefined_skills)  # Find matching skills

    # Find similar skills using fuzzy matching
    for word in words:
        close_matches = get_close_matches(word, predefined_skills, n=1, cutoff=0.8)
        matched_skills.update(close_matches)

    # Find partial matches using regex
    for skill in predefined_skills:
        pattern = rf"\b{skill.split()[0]}\b"  # Match the first word of the skill
        if re.search(pattern, resume_text):
            matched_skills.add(skill)
        
    return list(matched_skills)

# Load dataset
df = pd.read_csv("synthetic_resumes_5000.csv")

# Combine relevant text fields for resume representation
resume_texts = df["Skills"] + " " + df["Education"] + " " + df["Certifications"]
job_descriptions = df["Job Description"]

# Initialize TF-IDF Vectorizer
vectorizer = TfidfVectorizer(stop_words="english")

# Fit and transform resumes and job descriptions into TF-IDF vectors
tfidf_resumes = vectorizer.fit_transform(resume_texts.apply(lambda x : clean_text(x)))
tfidf_jobs = vectorizer.transform(job_descriptions.apply(lambda x : clean_text(x)))

# Compute Cosine Similarity between resumes and job descriptions
similarity_scores = cosine_similarity(tfidf_resumes, tfidf_jobs)

# Extract diagonal values where resumes are compared to their respective job descriptions
df["TF-IDF Score"] = np.diag(similarity_scores)

# Rank resumes based on similarity score
df_sorted = df.sort_values(by="TF-IDF Score", ascending=False)

# Save ranked results to a new CSV file
# df_sorted.to_csv("ranked_resumes_tfidf.csv", index=False)

print("Resume ranking complete. Check 'ranked_resumes_tfidf.csv' for results.")

@app.route('/predict', methods=['POST'])
def predict():
    job_desc = request.form['job_description']
    skills_json = request.form.get('skills')
    required_skills = json.loads(skills_json)  # Deserialize the JSON string
    files = request.files.getlist("resumes")
    ranked_resumes = []
    predefined_skills = set(required_skills)
    
    for file in files:
        filename = file.filename

        real_resume_text = extract_text_from_pdf(file)
        real_job_description = clean_text(job_desc)
        # skills = extract_resume_info(real_resume_text)
        similarity_score = rank_real_resume(real_resume_text, real_job_description, vectorizer)
        skills = extract_relevant_skills(real_resume_text, predefined_skills) or "none"
        # job_category_prediction = predict_job_category(real_resume_text, df, vectorizer)

        ranked_resumes.append({
            "filename": filename,
            "skills": skills,
            "score": round(similarity_score, 2),
            # "predicted_category": predicted_category
        })

    ranked_resumes.sort(key=lambda x: x["score"], reverse=True)

    return jsonify(ranked_resumes)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
