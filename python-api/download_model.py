"""
Download BERT Model Script
Pre-downloads the BERT model to avoid runtime errors
"""

import os
import sys

def download_model():
    """Download the BERT model for sentence transformers"""

    print("=" * 60)
    print("BERT Model Downloader")
    print("=" * 60)

    # Set HuggingFace endpoint to ensure proper URL construction
    os.environ['HF_ENDPOINT'] = os.getenv('HF_ENDPOINT', 'https://huggingface.co')
    print(f"HuggingFace Endpoint: {os.environ['HF_ENDPOINT']}")

    try:
        from sentence_transformers import SentenceTransformer
        from config.model_config import BERT_CONFIG

        model_name = BERT_CONFIG['model_name']
        cache_dir = BERT_CONFIG['cache_dir']

        print(f"\nModel: {model_name}")
        print(f"Cache Directory: {cache_dir or 'default (~/.cache/torch/sentence_transformers)'}")
        print("\nDownloading model... This may take a few minutes on first run.")
        print("-" * 60)

        # Download and cache the model
        model = SentenceTransformer(
            model_name,
            cache_folder=cache_dir
        )

        print("-" * 60)
        print("✅ Model downloaded successfully!")
        print(f"✅ Model info: {model}")

        # Test the model
        print("\nTesting model with sample text...")
        test_embedding = model.encode("This is a test sentence.")
        print(f"✅ Test successful! Embedding shape: {test_embedding.shape}")

        print("\n" + "=" * 60)
        print("SUCCESS: Model is ready to use!")
        print("=" * 60)

        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ ERROR: Failed to download model")
        print("=" * 60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify HF_ENDPOINT is set correctly:")
        print("   export HF_ENDPOINT=https://huggingface.co")
        print("3. If behind a proxy, configure proxy settings")
        print("4. Try using a mirror:")
        print("   export HF_ENDPOINT=https://hf-mirror.com")
        print("5. Or download manually and use offline mode:")
        print("   export HF_HUB_OFFLINE=1")
        print("=" * 60)

        return False


if __name__ == '__main__':
    success = download_model()
    sys.exit(0 if success else 1)
