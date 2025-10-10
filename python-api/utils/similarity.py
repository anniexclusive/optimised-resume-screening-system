from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skill_edu import degree_equivalents

# Initialize model as None and load it when needed
bert_model = None

def get_model():
    """Get or initialize the BERT model."""
    global bert_model
    if bert_model is None:
        bert_model = SentenceTransformer('all-MiniLM-L6-v2')
    return bert_model

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
    model = get_model()
    embedding1 = model.encode(text1).reshape(1, -1)
    embedding2 = model.encode(text2).reshape(1, -1)
    return cosine_similarity(embedding1, embedding2)[0][0]