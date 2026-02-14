import librosa
import soundfile as sf
import numpy as np
from scipy.signal import butter, filtfilt
import os
from pathlib import Path
from typing import Tuple, Dict, Any


class AudioProcessor:
    """Utility class for audio processing operations"""
    
    def __init__(self, sample_rate: int = 22050):
        self.sample_rate = sample_rate
    
    def load_audio(self, file_path: str, target_sr: int = None) -> Tuple[np.ndarray, int]:
        """
        Load audio file and return waveform and sample rate
        
        Args:
            file_path: Path to audio file
            target_sr: Target sample rate for resampling
            
        Returns:
            Tuple of (audio_data, sample_rate)
        """
        if target_sr is None:
            target_sr = self.sample_rate
            
        audio, sr = librosa.load(file_path, sr=target_sr, mono=True)
        return audio, sr
    
    def save_audio(self, audio_data: np.ndarray, output_path: str, sample_rate: int = None) -> None:
        """
        Save audio data to file
        
        Args:
            audio_data: Audio waveform as numpy array
            output_path: Path to save the audio file
            sample_rate: Sample rate of the audio
        """
        if sample_rate is None:
            sample_rate = self.sample_rate
            
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Normalize audio to prevent clipping
        audio_data = self.normalize_audio(audio_data)
        
        sf.write(output_path, audio_data, sample_rate)
    
    def normalize_audio(self, audio: np.ndarray, target_level: float = -20.0) -> np.ndarray:
        """
        Normalize audio to target level in dB
        
        Args:
            audio: Input audio waveform
            target_level: Target level in dB
            
        Returns:
            Normalized audio
        """
        # Calculate current RMS
        rms = np.sqrt(np.mean(audio**2))
        
        if rms == 0:
            return audio
        
        # Calculate target RMS from dB
        target_rms = 10 ** (target_level / 20)
        
        # Apply normalization
        normalized = audio * (target_rms / rms)
        
        # Prevent clipping
        max_val = np.abs(normalized).max()
        if max_val > 1.0:
            normalized = normalized / max_val * 0.99
            
        return normalized
    
    def reduce_noise(self, audio: np.ndarray, noise_threshold: float = 0.02) -> np.ndarray:
        """
        Simple noise reduction using spectral gating
        
        Args:
            audio: Input audio waveform
            noise_threshold: Threshold for noise gate
            
        Returns:
            Noise-reduced audio
        """
        # Compute STFT
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        # Estimate noise floor from first few frames
        noise_floor = np.median(magnitude[:, :10], axis=1, keepdims=True)
        
        # Apply spectral gate
        mask = magnitude > (noise_floor * (1 + noise_threshold))
        magnitude_cleaned = magnitude * mask
        
        # Reconstruct audio
        stft_cleaned = magnitude_cleaned * np.exp(1j * phase)
        audio_cleaned = librosa.istft(stft_cleaned)
        
        return audio_cleaned
    
    def apply_highpass_filter(self, audio: np.ndarray, cutoff: float = 80.0, order: int = 5) -> np.ndarray:
        """
        Apply high-pass filter to remove low-frequency noise
        
        Args:
            audio: Input audio waveform
            cutoff: Cutoff frequency in Hz
            order: Filter order
            
        Returns:
            Filtered audio
        """
        nyquist = self.sample_rate / 2
        normal_cutoff = cutoff / nyquist
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        filtered = filtfilt(b, a, audio)
        return filtered
    
    def trim_silence(self, audio: np.ndarray, top_db: int = 30) -> np.ndarray:
        """
        Trim silence from beginning and end of audio
        
        Args:
            audio: Input audio waveform
            top_db: Threshold in dB below reference to consider as silence
            
        Returns:
            Trimmed audio
        """
        trimmed, _ = librosa.effects.trim(audio, top_db=top_db)
        return trimmed
    
    def validate_audio_quality(self, audio: np.ndarray, min_duration: float = 1.0) -> Dict[str, Any]:
        """
        Validate audio quality and return metrics
        
        Args:
            audio: Input audio waveform
            min_duration: Minimum required duration in seconds
            
        Returns:
            Dictionary with validation results
        """
        duration = len(audio) / self.sample_rate
        rms = np.sqrt(np.mean(audio**2))
        peak = np.abs(audio).max()
        
        # Calculate SNR estimate
        noise_estimate = np.std(audio[:int(0.1 * self.sample_rate)])  # First 100ms
        signal_estimate = np.std(audio)
        snr_value = 20 * np.log10(signal_estimate / (noise_estimate + 1e-10))
        
        validation = {
            "is_valid": True,
            "duration": duration,
            "rms": float(rms),
            "peak": float(peak),
            "snr_db": float(snr_value),
            "issues": []
        }
        
        if duration < min_duration:
            validation["is_valid"] = False
            validation["issues"].append(f"Audio too short: {duration:.2f}s (minimum: {min_duration}s)")
        
        if rms < 0.01:
            validation["is_valid"] = False
            validation["issues"].append("Audio level too low")
        
        if peak > 0.99:
            validation["issues"].append("Audio may be clipping")
        
        if snr_value < 10:
            validation["issues"].append("Low signal-to-noise ratio")
        
        return validation
    
    def preprocess_for_tts(self, audio: np.ndarray) -> np.ndarray:
        """
        Complete preprocessing pipeline for TTS training
        
        Args:
            audio: Input audio waveform
            
        Returns:
            Preprocessed audio
        """
        # Trim silence
        audio = self.trim_silence(audio)
        
        # Apply high-pass filter
        audio = self.apply_highpass_filter(audio)
        
        # Reduce noise
        audio = self.reduce_noise(audio)
        
        # Normalize
        audio = self.normalize_audio(audio)
        
        return audio
