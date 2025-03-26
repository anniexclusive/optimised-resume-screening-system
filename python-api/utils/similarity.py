from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.skill_edu import degree_equivalents

# Load pre-trained BERT model for embeddings
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

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