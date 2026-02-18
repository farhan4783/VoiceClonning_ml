from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from typing import Optional
import shutil
import logging
from datetime import datetime
import uvicorn

from config import settings
from tts_engine import TTSEngine
from voice_cloner import VoiceCloner
from utils.audio_utils import AudioProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
tts_engine = TTSEngine(use_gpu=settings.USE_GPU)
voice_cloner = VoiceCloner(models_dir=str(settings.MODELS_DIR))
audio_processor = AudioProcessor(sample_rate=settings.SAMPLE_RATE)

# Pydantic models
class SynthesisRequest(BaseModel):
    text: str
    model_id: Optional[str] = None
    language: str = "en"

class ModelUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# API Endpoints

@app.get("/")
async def root():
    """Redirect to API documentation"""
    return RedirectResponse(url="/docs")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        model_info = tts_engine.get_model_info()
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "tts_engine": model_info
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/upload-voice")
async def upload_voice(
    file: UploadFile = File(...),
    model_name: str = Form(...),
    description: str = Form("")
):
    """
    Upload voice sample and create voice model
    
    Args:
        file: Audio file (WAV recommended, 30+ seconds)
        model_name: Name for the voice model
        description: Optional description
    """
    try:
        logger.info(f"Received voice upload: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Supported: WAV, MP3, M4A, FLAC"
            )
        
        # Validate file size (e.g., max 10MB)
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size is 10MB."
            )
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = settings.UPLOAD_DIR / f"{timestamp}_{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File saved: {file_path}")
        
        # Convert to WAV if needed
        if not file.filename.lower().endswith('.wav'):
            wav_path = file_path.with_suffix('.wav')
            audio, sr = audio_processor.load_audio(str(file_path))
            audio_processor.save_audio(audio, str(wav_path))
            file_path = wav_path
        
        # Create voice model
        result = voice_cloner.create_voice_model(
            audio_path=str(file_path),
            model_name=model_name,
            description=description
        )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Voice model created successfully",
                "model": result["model_info"]
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
async def synthesize_speech(request: SynthesisRequest):
    """
    Synthesize speech from text
    
    Args:
        request: Synthesis request with text and optional model_id
    """
    try:
        logger.info(f"Synthesis request: {request.text[:50]}...")
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"synthesis_{timestamp}.wav"
        output_path = settings.OUTPUT_DIR / output_filename
        
        # Get reference audio if model specified
        speaker_wav = None
        if request.model_id:
            model = voice_cloner.get_model(request.model_id)
            if model and model.get("reference_audio"):
                speaker_wav = model["reference_audio"]
                logger.info(f"Using voice model: {model['name']}")
        
        # Synthesize speech
        if speaker_wav:
            result = tts_engine.clone_voice(
                text=request.text,
                reference_audio=speaker_wav,
                output_path=str(output_path),
                language=request.language
            )
        else:
            result = tts_engine.synthesize_speech(
                text=request.text,
                output_path=str(output_path),
                language=request.language
            )
        
        if result["success"]:
            return {
                "success": True,
                "message": "Speech synthesized successfully",
                "audio_url": f"/audio/{output_filename}",
                "details": result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "Synthesis failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_models():
    """Get all available voice models"""
    try:
        models = voice_cloner.get_all_models()
        return {
            "success": True,
            "count": len(models),
            "models": models
        }
    except Exception as e:
        logger.error(f"Error getting models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models/{model_id}")
async def get_model(model_id: str):
    """Get specific voice model"""
    model = voice_cloner.get_model(model_id)
    if model:
        return {
            "success": True,
            "model": model
        }
    else:
        raise HTTPException(status_code=404, detail="Model not found")

@app.put("/models/{model_id}")
async def update_model(model_id: str, request: ModelUpdateRequest):
    """Update voice model information"""
    try:
        result = voice_cloner.update_model_info(
            model_id=model_id,
            name=request.name,
            description=request.description
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Update failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/models/{model_id}")
async def delete_model(model_id: str):
    """Delete voice model"""
    try:
        result = voice_cloner.delete_model(model_id)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Deletion failed"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    """Serve generated audio files"""
    file_path = settings.OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        path=file_path,
        media_type="audio/wav",
        filename=filename
    )

@app.get("/tts/info")
async def get_tts_info():
    """Get TTS engine information"""
    return tts_engine.get_model_info()


# Run server
if __name__ == "__main__":
    logger.info(f"Starting {settings.APP_NAME} on {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
