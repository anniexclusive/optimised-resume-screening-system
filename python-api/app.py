from flask import Flask, request, jsonify
from utils.pdf_processing import extract_text_from_pdf
from utils.text_processing import clean_text, remove_sensitive_info, fix_broken_words
from utils.extraction import extract_entities, filter_skills, extract_experience, get_years, extract_num_years, get_education_text
from utils.similarity import compute_similarity, qualification_similarity
from utils.scoring import get_resume_ranking_score, generate_explanation, compute_experience_score

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"}), 200

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
    
    for file in files:

        resume_text = extract_text_from_pdf(file)
        
        ranking_data = extract_entities(resume_text)
        ranking_data['r_skills'] = filter_skills(ranking_data['skills'], job_data['skills'])
        ranking_data["resume_text"] = remove_sensitive_info(clean_text(resume_text)) # remove bias
        ranking_data = {k: ", ".join(v) if isinstance(v, (set, tuple)) else v for k, v in ranking_data.items()}
        ranking_data["filename"] = file.filename

        scores = get_resume_ranking_score(ranking_data, job_data)
        ranking_data["explanation"] = generate_explanation(scores, job_data)
        # Drop the key 'resume_text'
        del ranking_data['resume_text']
        
        result = ranking_data | scores # combines the two data

        ranked_resumes.append(result)

    ranked_resumes.sort(key=lambda x: x["ts"], reverse=True)

    return jsonify(ranked_resumes)
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)