from flask import Flask, request, jsonify
import fitz

app = Flask(__name__)

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

@app.route('/predict', methods=['POST'])
def predict():
    files = request.files.getlist('files')  # Accept multiple files
    results = {}

    for file in files:
        pdf_path = f"temp_{file.filename}"
        file.save(pdf_path)
        resume_text = extract_text_from_pdf(pdf_path)
        results[file.filename] = {"score": 85, "category": "Software Engineer"}  # Replace with model logic

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
