"""
MixMaster Pro - Configuration Settings
Development mode (no Docker)
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "MixMaster Pro"
    VERSION: str = "1.0.0-dev"
    DEBUG: bool = True
    
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Database (SQLite for development)
    DATABASE_URL: str = "sqlite:///./mixmaster.db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Backblaze B2
    B2_APPLICATION_KEY_ID: str
    B2_APPLICATION_KEY: str
    B2_BUCKET_INPUT: str = "mixmaster-input"
    B2_BUCKET_OUTPUT: str = "mixmaster-output"
    B2_BUCKET_REPORTS: str = "mixmaster-reports"
    
    # Audio Processing
    MAX_STEMS: int = 12
    MAX_FILE_SIZE_MB: int = 500
    SAMPLE_RATE: int = 48000
    BIT_DEPTH: int = 24
    
    # Processing Performance
    CHUNK_SIZE_SECONDS: float = 25.0
    OVERLAP_SECONDS: float = 0.3
    USE_GPU: bool = True
    PROCESSING_TIMEOUT: int = 600  # 10 minutes
    
    # Safety Limits
    MAX_EQ_GAIN_DB: float = 4.0
    MAX_AVG_GR_DB: float = 3.0
    TRUE_PEAK_CEILING_DBTP: float = -1.0
    MAX_STEREO_WIDTH_PCT: int = 140
    MIN_MONO_CORRELATION: float = 0.1
    
    # LUFS Targets
    LUFS_STREAMING: float = -14.0
    LUFS_POP: float = -10.0
    LUFS_CLUB: float = -8.0
    
    # Paths
    TEMP_DIR: str = "./temp"
    PRESETS_DIR: str = "./config/presets"
    MODELS_DIR: str = "./ml_models/checkpoints"
    
    class Config:
        env_file = "../.env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Global settings instance
settings = Settings()


# Ensure directories exist
os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs(settings.PRESETS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
