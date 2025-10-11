"""
ML Model Configuration
Centralized configuration for machine learning models
"""

import os

# BERT Model Configuration
BERT_CONFIG = {
    'model_name': os.getenv('BERT_MODEL', 'all-MiniLM-L6-v2'),
    'cache_dir': os.getenv('MODEL_CACHE_DIR', None),
    'device': os.getenv('MODEL_DEVICE', None),  # None = auto-detect (CPU/GPU)
    'max_seq_length': int(os.getenv('MAX_SEQ_LENGTH', 256))
}

# Model Loading Configuration
MODEL_LOAD_CONFIG = {
    'lazy_loading': os.getenv('LAZY_LOAD_MODEL', 'true').lower() == 'true',
    'show_progress_bar': os.getenv('SHOW_PROGRESS', 'false').lower() == 'true'
}

# Flask App Configuration
FLASK_CONFIG = {
    'host': os.getenv('FLASK_HOST', '0.0.0.0'),
    'port': int(os.getenv('FLASK_PORT', 5000)),
    'debug': os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
}

def get_model_config():
    """Returns the current BERT model configuration"""
    return BERT_CONFIG.copy()

def get_flask_config():
    """Returns the current Flask configuration"""
    return FLASK_CONFIG.copy()
