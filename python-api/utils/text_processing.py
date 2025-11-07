"""
Text processing utilities with optimized performance
"""
import re
import logging

logger = logging.getLogger(__name__)

# English stopwords - hardcoded to avoid NLTK dependency
STOP_WORDS = {
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
    "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he',
    'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's",
    'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
    'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do',
    'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because',
    'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
    'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
    'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd', 'll', 'm',
    'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn', "couldn't", 'didn',
    "didn't", 'doesn', "doesn't", 'hadn', "hadn't", 'hasn', "hasn't", 'haven',
    "haven't", 'isn', "isn't", 'ma', 'mightn', "mightn't", 'mustn', "mustn't",
    'needn', "needn't", 'shan', "shan't", 'shouldn', "shouldn't", 'wasn', "wasn't",
    'weren', "weren't", 'won', "won't", 'wouldn', "wouldn't"
}

# Pre-compile regex patterns for better performance
SPECIAL_CHARS_PATTERN = re.compile(r'[^a-zA-Z0-9\s]')
WHITESPACE_PATTERN = re.compile(r'\s+')
SHORT_SPLIT_PATTERN = re.compile(r'(\w)(?=\s{1,2}\w)')
BROKEN_WORDS_PATTERN = re.compile(r'(\b\w{1,10})\s(?=\w{1,10}\b)')
LETTER_NUMBER_PATTERN = re.compile(r'([a-zA-Z])(\d)')
NUMBER_LETTER_PATTERN = re.compile(r'(\d)([a-zA-Z])')
MONTH_NAMES = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec|" \
              r"January|February|March|April|May|June|July|August|September|" \
              r"October|November|December)"
MONTH_PATTERN = re.compile(r'(\w)(' + MONTH_NAMES + r')', flags=re.IGNORECASE)


def clean_text(text: str) -> str:
    """
    Cleans the extracted text by removing special characters, numbers, and stopwords.

    Args:
        text: Input text to clean

    Returns:
        Cleaned text string

    Performance: Pre-compiled regex patterns, optimized string operations
    """
    # Check if the text is valid and non-empty
    if not text or not text.strip():
        return ""

    # Convert to lowercase
    text = text.lower()

    # Remove special characters (pre-compiled pattern)
    text = SPECIAL_CHARS_PATTERN.sub('', text)

    # Remove stopwords (optimized with set comprehension)
    words = text.split()
    text = " ".join(word for word in words if word not in STOP_WORDS)

    return text


def remove_sensitive_info(text: str) -> str:
    """
    Removes potential bias-related words from resume text.

    Args:
        text: Input text

    Returns:
        Text with sensitive information removed

    Note: This is a basic implementation. For production, consider
    using NER (Named Entity Recognition) for better accuracy.
    """
    if not text:
        return ""

    bias_keywords = [
        "male", "female", "black", "white", "asian",
        "african", "hispanic", "married", "single"
    ]

    # Use word boundaries to avoid partial word matches
    for word in bias_keywords:
        pattern = re.compile(r'\b' + word + r'\b', flags=re.IGNORECASE)
        text = pattern.sub(' ', text)

    # Clean up extra spaces
    text = WHITESPACE_PATTERN.sub(' ', text).strip()

    return text


def fix_broken_words(text: str) -> str:
    """
    Fixes broken words by merging improperly split words.
    Also removes extra spaces.

    Args:
        text: Input text with potential broken words

    Returns:
        Text with fixed word breaks

    Performance: Uses pre-compiled regex patterns
    """
    if not text:
        return ""

    # Remove extra whitespace everywhere (pre-compiled pattern)
    text = WHITESPACE_PATTERN.sub(' ', text).strip()

    # Add space between a letter and a number (e.g., "september2011" -> "september 2011")
    text = LETTER_NUMBER_PATTERN.sub(r'\1 \2', text)

    # Add space between a number and a letter (e.g., "2011newbrunswick" -> "2011 newbrunswick")
    text = NUMBER_LETTER_PATTERN.sub(r'\1 \2', text)

    # Add space before any month name (e.g., "newbrunswickseptember" -> "newbrunswick september")
    text = MONTH_PATTERN.sub(r'\1 \2', text)

    return text
