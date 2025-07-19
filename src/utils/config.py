"""Configuration management for the recruitment POC."""
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables."""
    return {
        # LLM Configuration
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY"),
        "openrouter_base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        
        # Database Configuration
        "database_url": os.getenv("DATABASE_URL"),
        
        # Redis Configuration
        "redis_host": os.getenv("REDIS_HOST", "localhost"),
        "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        "redis_password": os.getenv("REDIS_PASSWORD", ""),
        "redis_channel": os.getenv("REDIS_CHANNEL", "hitl_queue"),
        
        # Milvus Lite Configuration
        "milvus_lite_file": os.getenv("MILVUS_LITE_FILE", "./milvus_lite.db"),
        "milvus_collection_name": os.getenv("MILVUS_COLLECTION_NAME", "recruitment_embeddings"),
        
        # Application Configuration
        "hitl_confidence_threshold": float(os.getenv("HITL_CONFIDENCE_THRESHOLD", "0.85")),
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
        "embedding_dimension": int(os.getenv("EMBEDDING_DIMENSION", "1536")),
        
        # API Configuration
        "api_host": os.getenv("API_HOST", "0.0.0.0"),
        "api_port": int(os.getenv("API_PORT", "8001")),
        "api_reload": os.getenv("API_RELOAD", "true").lower() == "true",
        
        # Chainlit Configuration
        "chainlit_host": os.getenv("CHAINLIT_HOST", "0.0.0.0"),
        "chainlit_port": int(os.getenv("CHAINLIT_PORT", "8000")),
        
        # Feature Flags
        "enable_bias_detection": os.getenv("ENABLE_BIAS_DETECTION", "true").lower() == "true",
        "enable_transferable_skills": os.getenv("ENABLE_TRANSFERABLE_SKILLS", "true").lower() == "true",
        "enable_audit_logging": os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true",
        
        # Development Settings
        "debug": os.getenv("DEBUG", "false").lower() == "true",
        "testing": os.getenv("TESTING", "false").lower() == "true",
    }

def validate_config(config: Dict[str, Any]) -> None:
    """Validate required configuration values."""
    required_keys = [
        "openai_api_key",
        "database_url",
    ]
    
    missing_keys = [key for key in required_keys if not config.get(key)]
    
    if missing_keys:
        raise ValueError(f"Missing required configuration: {', '.join(missing_keys)}")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = SRC_DIR / "data"
TESTS_DIR = PROJECT_ROOT / "tests"