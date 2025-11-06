"""
Model Configuration
Centralizes all ML model configuration
Following SOLID principles - Single Responsibility & Open/Closed
"""
import os

# BERT Model Configuration
BERT_CONFIG = {
    'model_name': os.getenv('BERT_MODEL', 'all-MiniLM-L6-v2'),
    'cache_dir': os.getenv('MODEL_CACHE_DIR', None),
    'device': os.getenv('MODEL_DEVICE', None),  # 'cuda', 'cpu', or None for auto
    'max_seq_length': int(os.getenv('MAX_SEQ_LENGTH', 256))
}

# Model Loading Configuration
MODEL_LOAD_CONFIG = {
    'lazy_loading': os.getenv('LAZY_LOAD_MODEL', 'true').lower() == 'true',
    'show_progress': os.getenv('SHOW_PROGRESS', 'false').lower() == 'true',
    'local_files_only': os.getenv('LOCAL_FILES_ONLY', 'false').lower() == 'true'
}

# Flask Configuration
FLASK_CONFIG = {
    'host': os.getenv('FLASK_HOST', '0.0.0.0'),
    'port': int(os.getenv('FLASK_PORT', 5000)),
    'debug': os.getenv('FLASK_DEBUG', 'false').lower() == 'true'  # Secure default: debug disabled in production
}


def get_model_config():
    """Helper function to get model configuration"""
    return BERT_CONFIG


def get_flask_config():
    """Helper function to get Flask configuration"""
    return FLASK_CONFIG
