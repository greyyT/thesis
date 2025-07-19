"""Configuration management for the recruitment system."""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_config() -> Dict[str, Any]:
    """Get configuration from environment variables."""
    return {
        # API Keys
        "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
        "openrouter_api_key": os.getenv("OPENROUTER_API_KEY", ""),
        
        # Database
        "database_url": os.getenv("DATABASE_URL", "postgresql://localhost/recruitment"),
        
        # Redis
        "redis_host": os.getenv("REDIS_HOST", "localhost"),
        "redis_port": int(os.getenv("REDIS_PORT", "6379")),
        "redis_db": int(os.getenv("REDIS_DB", "0")),
        
        # Milvus
        "milvus_lite_file": os.getenv("MILVUS_LITE_FILE", "./milvus_lite.db"),
        "milvus_collection_name": os.getenv("MILVUS_COLLECTION_NAME", "recruitment_embeddings"),
        
        # Agent Configuration
        "hitl_confidence_threshold": float(os.getenv("HITL_CONFIDENCE_THRESHOLD", "0.85")),
        "embedding_dimension": int(os.getenv("EMBEDDING_DIMENSION", "1536")),
        "embedding_model": os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        
        # Feature Flags
        "enable_bias_detection": os.getenv("ENABLE_BIAS_DETECTION", "true").lower() == "true",
        "enable_audit_logging": os.getenv("ENABLE_AUDIT_LOGGING", "true").lower() == "true",
        
        # UI Configuration
        "ui_port": int(os.getenv("UI_PORT", "8000")),
        "ui_host": os.getenv("UI_HOST", "0.0.0.0"),
    }


def validate_config(config: Dict[str, Any]) -> bool:
    """Validate required configuration values."""
    required_keys = [
        "openai_api_key",
        "database_url",
        "redis_host",
        "redis_port"
    ]
    
    missing_keys = []
    for key in required_keys:
        if not config.get(key):
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing required configuration: {', '.join(missing_keys)}")
        print("Please check your .env file")
        return False
    
    return True