import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "VoiceClone Studio API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Model Settings
    TTS_MODEL_NAME: str = "tts_models/en/ljspeech/tacotron2-DDC"
    VOCODER_MODEL_NAME: str = "vocoder_models/en/ljspeech/hifigan_v2"
    USE_GPU: bool = False
    
    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MODELS_DIR: Path = BASE_DIR / "models"
    OUTPUT_DIR: Path = BASE_DIR / "outputs"
    
    # Audio Settings
    MAX_AUDIO_LENGTH: int = 60
    SAMPLE_RATE: int = 22050

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Ensure directories exist
for directory in [settings.UPLOAD_DIR, settings.MODELS_DIR, settings.OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
