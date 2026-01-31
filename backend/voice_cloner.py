import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import logging
from utils.audio_utils import AudioProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceCloner:
    """Manages voice models and cloning operations"""
    
    def __init__(self, models_dir: str = "./models"):
        """
        Initialize Voice Cloner
        
        Args:
            models_dir: Directory to store voice models
        """
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.audio_processor = AudioProcessor()
        self.metadata_file = self.models_dir / "models_metadata.json"
        
        # Load or initialize metadata
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """Load models metadata from file"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {"models": {}}
        return {"models": {}}
    
    def _save_metadata(self):
        """Save models metadata to file"""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def create_voice_model(
        self,
        audio_path: str,
        model_name: str,
        description: str = ""
    ) -> Dict:
        """
        Create a new voice model from audio sample
        
        Args:
            audio_path: Path to reference audio file
            model_name: Name for the voice model
            description: Optional description
            
        Returns:
            Dictionary with model information
        """
        try:
            logger.info(f"Creating voice model: {model_name}")
            
            # Validate audio
            audio, sr = self.audio_processor.load_audio(audio_path)
            validation = self.audio_processor.validate_audio_quality(audio, min_duration=10.0)
            
            if not validation["is_valid"]:
                return {
                    "success": False,
                    "error": "Audio quality validation failed",
                    "issues": validation["issues"]
                }
            
            # Preprocess audio
            processed_audio = self.audio_processor.preprocess_for_tts(audio)
            
            # Create model directory
            model_id = self._generate_model_id(model_name)
            model_dir = self.models_dir / model_id
            model_dir.mkdir(parents=True, exist_ok=True)
            
            # Save processed audio as reference
            reference_path = model_dir / "reference.wav"
            self.audio_processor.save_audio(processed_audio, str(reference_path))
            
            # Create metadata entry
            model_info = {
                "id": model_id,
                "name": model_name,
                "description": description,
                "created_at": datetime.now().isoformat(),
                "reference_audio": str(reference_path),
                "duration": validation["duration"],
                "quality_metrics": {
                    "snr_db": validation["snr_db"],
                    "rms": validation["rms"]
                },
                "type": "custom"
            }
            
            # Save metadata
            self.metadata["models"][model_id] = model_info
            self._save_metadata()
            
            logger.info(f"Voice model created successfully: {model_id}")
            
            return {
                "success": True,
                "model_id": model_id,
                "model_info": model_info
            }
            
        except Exception as e:
            logger.error(f"Error creating voice model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_model_id(self, model_name: str) -> str:
        """Generate unique model ID from name"""
        # Clean name and add timestamp
        clean_name = "".join(c if c.isalnum() else "_" for c in model_name.lower())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{clean_name}_{timestamp}"
    
    def get_model(self, model_id: str) -> Optional[Dict]:
        """
        Get voice model information
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model information or None
        """
        return self.metadata["models"].get(model_id)
    
    def get_all_models(self) -> List[Dict]:
        """Get all available voice models"""
        return list(self.metadata["models"].values())
    
    def delete_model(self, model_id: str) -> Dict:
        """
        Delete a voice model
        
        Args:
            model_id: Model identifier
            
        Returns:
            Dictionary with deletion result
        """
        try:
            if model_id not in self.metadata["models"]:
                return {
                    "success": False,
                    "error": "Model not found"
                }
            
            # Delete model directory
            model_dir = self.models_dir / model_id
            if model_dir.exists():
                shutil.rmtree(model_dir)
            
            # Remove from metadata
            del self.metadata["models"][model_id]
            self._save_metadata()
            
            logger.info(f"Model deleted: {model_id}")
            
            return {
                "success": True,
                "message": "Model deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_model_info(self, model_id: str, name: str = None, description: str = None) -> Dict:
        """
        Update voice model information
        
        Args:
            model_id: Model identifier
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            Dictionary with update result
        """
        try:
            if model_id not in self.metadata["models"]:
                return {
                    "success": False,
                    "error": "Model not found"
                }
            
            if name:
                self.metadata["models"][model_id]["name"] = name
            
            if description is not None:
                self.metadata["models"][model_id]["description"] = description
            
            self.metadata["models"][model_id]["updated_at"] = datetime.now().isoformat()
            self._save_metadata()
            
            return {
                "success": True,
                "model_info": self.metadata["models"][model_id]
            }
            
        except Exception as e:
            logger.error(f"Error updating model: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def add_preset_voices(self):
        """Add preset celebrity/character voices (placeholder for future implementation)"""
        presets = [
            {
                "id": "preset_morgan_freeman",
                "name": "Morgan Freeman",
                "description": "Deep, authoritative voice",
                "type": "preset",
                "created_at": datetime.now().isoformat()
            },
            {
                "id": "preset_david_attenborough",
                "name": "David Attenborough",
                "description": "Nature documentary style",
                "type": "preset",
                "created_at": datetime.now().isoformat()
            }
        ]
        
        for preset in presets:
            if preset["id"] not in self.metadata["models"]:
                self.metadata["models"][preset["id"]] = preset
        
        self._save_metadata()
        logger.info("Preset voices added")
