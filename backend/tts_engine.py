import os
import torch
import numpy as np
from TTS.api import TTS
from pathlib import Path
import logging
from typing import Optional, Dict
from utils.audio_utils import AudioProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TTSEngine:
    """Text-to-Speech engine using Coqui TTS"""
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize TTS engine
        
        Args:
            use_gpu: Whether to use GPU acceleration
        """
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing TTS Engine on {self.device}")
        
        self.audio_processor = AudioProcessor()
        self.tts = None
        self.current_model = None
        
        # Initialize with default model
        self._load_default_model()
    
    def _load_default_model(self):
        """Load the default TTS model"""
        try:
            # Using XTTS-v2 for voice cloning capabilities
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            logger.info(f"Loading model: {model_name}")
            
            self.tts = TTS(model_name).to(self.device)
            self.current_model = model_name
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading default model: {e}")
            # Fallback to simpler model
            try:
                model_name = "tts_models/en/ljspeech/tacotron2-DDC"
                logger.info(f"Falling back to: {model_name}")
                self.tts = TTS(model_name).to(self.device)
                self.current_model = model_name
            except Exception as e2:
                logger.error(f"Error loading fallback model: {e2}")
                raise
    
    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        speaker_wav: Optional[str] = None,
        language: str = "en"
    ) -> Dict:
        """
        Synthesize speech from text
        
        Args:
            text: Text to synthesize
            output_path: Path to save output audio
            speaker_wav: Path to reference speaker audio for voice cloning
            language: Language code
            
        Returns:
            Dictionary with synthesis results
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            logger.info(f"Synthesizing: '{text[:50]}...'")
            
            if speaker_wav and os.path.exists(speaker_wav):
                # Voice cloning mode
                logger.info(f"Using speaker reference: {speaker_wav}")
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path,
                    speaker_wav=speaker_wav,
                    language=language
                )
            else:
                # Default voice mode
                logger.info("Using default voice")
                self.tts.tts_to_file(
                    text=text,
                    file_path=output_path
                )
            
            # Validate output
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                logger.info(f"Synthesis complete. Output size: {file_size} bytes")
                
                return {
                    "success": True,
                    "output_path": output_path,
                    "file_size": file_size,
                    "text_length": len(text),
                    "model": self.current_model
                }
            else:
                raise Exception("Output file was not created")
                
        except Exception as e:
            logger.error(f"Synthesis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clone_voice(
        self,
        text: str,
        reference_audio: str,
        output_path: str,
        language: str = "en"
    ) -> Dict:
        """
        Clone a voice and synthesize speech
        
        Args:
            text: Text to synthesize
            reference_audio: Path to reference audio (30s recommended)
            output_path: Path to save output
            language: Language code
            
        Returns:
            Dictionary with results
        """
        logger.info(f"Voice cloning with reference: {reference_audio}")
        
        # Preprocess reference audio
        try:
            audio, sr = self.audio_processor.load_audio(reference_audio)
            
            # Validate audio quality
            validation = self.audio_processor.validate_audio_quality(audio, min_duration=5.0)
            
            if not validation["is_valid"]:
                logger.warning(f"Audio quality issues: {validation['issues']}")
                # Continue anyway but log the issues
            
            # Preprocess audio
            processed_audio = self.audio_processor.preprocess_for_tts(audio)
            
            # Save processed audio temporarily
            temp_path = reference_audio.replace(".wav", "_processed.wav")
            self.audio_processor.save_audio(processed_audio, temp_path)
            
            # Synthesize with cloned voice
            result = self.synthesize_speech(
                text=text,
                output_path=output_path,
                speaker_wav=temp_path,
                language=language
            )
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            if result["success"]:
                result["audio_quality"] = validation
            
            return result
            
        except Exception as e:
            logger.error(f"Voice cloning error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_available_models(self) -> list:
        """Get list of available TTS models"""
        try:
            models = TTS().list_models()
            return models
        except Exception as e:
            logger.error(f"Error getting models: {e}")
            return []
    
    def get_model_info(self) -> Dict:
        """Get information about current model"""
        return {
            "model_name": self.current_model,
            "device": self.device,
            "gpu_available": torch.cuda.is_available()
        }
