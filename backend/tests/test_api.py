from fastapi.testclient import TestClient
import pytest
from unittest.mock import MagicMock, patch
import logging

# Check if main can be imported, which depends on config and other modules
try:
    from main import app
    from config import settings
except ImportError:
    # If running from tests/ directory, we might need to adjust path or this might fail
    # This is just a basic check
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from main import app
    from config import settings

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }

@patch('main.tts_engine')
def test_health_check(mock_tts_engine):
    mock_tts_engine.get_model_info.return_value = {"model": "test_model"}
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["tts_engine"] == {"model": "test_model"}

def test_upload_invalid_file_type():
    # Test uploading a text file instead of audio
    files = {'file': ('test.txt', b'test content', 'text/plain')}
    data = {'model_name': 'test_voice'}
    response = client.post("/upload-voice", files=files, data=data)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]

def test_get_models_empty():
    # Mock voice_cloner to return empty list
    with patch('main.voice_cloner') as mock_voice_cloner:
        mock_voice_cloner.get_all_models.return_value = []
        response = client.get("/models")
        assert response.status_code == 200
        assert response.json()["count"] == 0
        assert response.json()["models"] == []

def test_synthesize_missing_text():
    response = client.post("/synthesize", json={})
    assert response.status_code == 422 # Validation Error
