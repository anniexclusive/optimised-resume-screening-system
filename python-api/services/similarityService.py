"""
Similarity Service
Abstraction layer for similarity computation
Implements Dependency Inversion Principle
"""

from abc import ABC, abstractmethod
from sentence_transformers import SentenceTransformer
import numpy as np
from config.model_config import BERT_CONFIG, MODEL_LOAD_CONFIG


class SimilarityCalculator(ABC):
    """Abstract base class for similarity calculators"""

    @abstractmethod
    def compute_similarity(self, text1, text2):
        """Compute similarity between two texts"""
        pass

    @abstractmethod
    def encode(self, text):
        """Encode text to embeddings"""
        pass


class BERTSimilarityCalculator(SimilarityCalculator):
    """BERT-based similarity calculator using SentenceTransformers"""

    def __init__(self, model_name=None, device=None, cache_dir=None):
        """
        Initialize BERT model

        Args:
            model_name: Name of the BERT model (defaults to config)
            device: Device to run model on (None = auto-detect)
            cache_dir: Directory to cache model files
        """
        self.model_name = model_name or BERT_CONFIG['model_name']
        self.device = device or BERT_CONFIG['device']
        self.cache_dir = cache_dir or BERT_CONFIG['cache_dir']
        self._model = None

        # Lazy loading if configured
        if not MODEL_LOAD_CONFIG['lazy_loading']:
            self._load_model()

    def _load_model(self):
        """Load the BERT model (lazy loading)"""
        if self._model is None:
            print(f"[SimilarityService] Loading model: {self.model_name}")
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
                cache_folder=self.cache_dir
            )
            print(f"[SimilarityService] Model loaded successfully")
        return self._model

    @property
    def model(self):
        """Get the model, loading it if necessary"""
        return self._load_model()

    def encode(self, text):
        """
        Encode text to embeddings

        Args:
            text: Text to encode

        Returns:
            numpy array of embeddings
        """
        return self.model.encode(text)

    def compute_similarity(self, text1, text2):
        """
        Compute cosine similarity between two texts

        Args:
            text1: First text
            text2: Second text

        Returns:
            float: Similarity score between 0 and 1
        """
        embedding1 = self.encode(text1)
        embedding2 = self.encode(text2)

        # Compute cosine similarity using numpy
        # cosine_similarity = dot(A, B) / (||A|| * ||B||)
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        similarity = dot_product / (norm1 * norm2)

        return float(similarity)


class MockSimilarityCalculator(SimilarityCalculator):
    """Mock similarity calculator for testing (always returns 0.8)"""

    def encode(self, text):
        """Mock encoding - returns dummy array"""
        return [0.1, 0.2, 0.3, 0.4]

    def compute_similarity(self, text1, text2):
        """Mock similarity - always returns 0.8"""
        return 0.8


# Singleton instance
_similarity_calculator = None


def get_similarity_calculator(calculator_type='bert'):
    """
    Get or create a similarity calculator instance

    Args:
        calculator_type: Type of calculator ('bert' or 'mock')

    Returns:
        SimilarityCalculator instance
    """
    global _similarity_calculator

    if _similarity_calculator is None:
        if calculator_type == 'bert':
            _similarity_calculator = BERTSimilarityCalculator()
        elif calculator_type == 'mock':
            _similarity_calculator = MockSimilarityCalculator()
        else:
            raise ValueError(f"Unknown calculator type: {calculator_type}")

    return _similarity_calculator


def reset_similarity_calculator():
    """Reset the singleton instance (useful for testing)"""
    global _similarity_calculator
    _similarity_calculator = None
