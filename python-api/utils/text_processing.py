"""
Text processing utilities with optimized performance
"""
import re
import nltk
from nltk.corpus import stopwords
import logging

logger = logging.getLogger(__name__)

# Download stopwords only if not already downloaded
try:
    stopwords.words("english")
    logger.debug("NLTK stopwords already downloaded")
except LookupError:
    logger.info("Downloading NLTK stopwords...")
    nltk.download('stopwords', quiet=True)

# Cache stopwords set for better performance
STOP_WORDS = set(stopwords.words("english"))

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
