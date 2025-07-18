import os
import warnings
import logging

# Suppress TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Suppress TensorFlow logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Disable tokenizers parallelism warning

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Suppress ChromaDB telemetry
os.environ['ANONYMIZED_TELEMETRY'] = 'false'

# Configure logging to reduce noise
logging.getLogger('chromadb').setLevel(logging.ERROR)
logging.getLogger('sentence_transformers').setLevel(logging.ERROR)
logging.getLogger('transformers').setLevel(logging.ERROR)
logging.getLogger('tensorflow').setLevel(logging.ERROR)

def setup_environment():
    """Setup environment variables and suppress warnings"""
    # Suppress OpenTelemetry warnings
    os.environ['OTEL_SDK_DISABLED'] = 'true'
    
    # Suppress HuggingFace warnings
    os.environ['TRANSFORMERS_VERBOSITY'] = 'error'
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    
    print("✅ Environment configured to suppress warnings")
