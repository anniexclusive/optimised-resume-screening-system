import re
import nltk
from nltk.corpus import stopwords
import pandas as pd

# Download stopwords if not already downloaded
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))

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

def fix_broken_words(text):
    """
    Fixes broken words by merging improperly split words.
    Also removes extra spaces.
    """
    # Fix cases like "w ork" -> "work", "wo rk" -> "work"
    text = re.sub(r'(\w)(?=\s{1,2}\w)', r'\1', text)   # Merges short split words

    # Remove extra whitespace everywhere
    text = re.sub(r'\s+', ' ', text).strip()

    # Step 2: Fix broken words (merge improperly split words)
    text = re.sub(r'(\b\w{1,10})\s(?=\w{1,10}\b)', r'\1', text)

    # Add space between a letter and a number (e.g., "september2011" -> "september 2011")
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)

    # Add space between a number and a letter (e.g., "2011newbrunswick" -> "2011 newbrunswick")
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)

    # Add space before any month name (e.g., "newbrunswickseptember" -> "newbrunswick september")
    months = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|" \
             r"January|February|March|April|May|June|July|August|September|" \
             r"October|November|December)"
    text = re.sub(r'(\w)(' + months + r')', r'\1 \2', text, flags=re.IGNORECASE)

    # Add space between a lowercase letter and an uppercase letter
    # text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    return text