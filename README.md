# VoiceClone Studio 🎙️

**Advanced Real-Time Voice Cloning & Synthesis powered by AI**

Clone your voice in just 30 seconds and generate speech in your own voice using cutting-edge AI technology!

![VoiceClone Studio](https://img.shields.io/badge/AI-Voice%20Cloning-blueviolet?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18+-61dafb?style=for-the-badge&logo=react)

## ✨ Features

- 🎤 **30-Second Voice Recording** - Quick and easy voice capture directly in your browser
- 🤖 **AI Voice Cloning** - Advanced neural synthesis using Coqui TTS
- 💬 **Text-to-Speech** - Generate speech in your cloned voice from any text
- 🎨 **Premium UI** - Beautiful glassmorphism design with smooth animations
- 📊 **Waveform Visualization** - Real-time audio visualization with WaveSurfer.js
- 🗂️ **Voice Library** - Manage multiple voice models
- 🌍 **Multi-language Support** - Synthesize speech in multiple languages
- 📥 **Download Audio** - Export generated speech as WAV files

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn
- (Optional) CUDA-capable GPU for faster processing

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create environment file:**
   ```bash
   copy .env.example .env
   ```
   Edit `.env` to configure settings (GPU usage, ports, etc.)

6. **Run the backend server:**
   ```bash
   python main.py
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## 📖 Usage Guide

### 1. Clone Your Voice

1. Click **"Start Recording"** in the Voice Recording Studio
2. Speak clearly for at least 30 seconds (longer is better)
3. Click **"Stop"** when finished
4. Preview your recording and click **"Create Voice Model"**
5. Enter a name and optional description
6. Wait for processing (2-5 minutes on CPU, 30-60s on GPU)

### 2. Synthesize Speech

1. Select a voice model from the Voice Library
2. Enter text in the Text-to-Speech section
3. Choose language (optional)
4. Click **"Synthesize Speech"**
5. Play or download the generated audio

### 3. Manage Voice Models

- **Edit**: Click the edit icon to rename or update description
- **Delete**: Click the trash icon to remove a voice model
- **Select**: Click on a card to select it for synthesis

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Coqui TTS** - Open-source text-to-speech engine
- **PyTorch** - Deep learning framework
- **librosa** - Audio processing
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **Vite** - Build tool
- **Framer Motion** - Animation library
- **WaveSurfer.js** - Audio visualization
- **Axios** - HTTP client

## 📁 Project Structure

```
Machine/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── tts_engine.py        # TTS engine wrapper
│   ├── voice_cloner.py      # Voice model management
│   ├── utils/
│   │   └── audio_utils.py   # Audio processing utilities
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment configuration template
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Hero.jsx           # Landing section
│   │   │   ├── VoiceRecorder.jsx  # Recording component
│   │   │   ├── VoiceLibrary.jsx   # Model management
│   │   │   └── TextToSpeech.jsx   # Synthesis component
│   │   ├── App.jsx          # Main application
│   │   ├── App.css          # Global styles
│   │   └── api.js           # API service
│   ├── package.json         # Node dependencies
│   └── .env                 # Frontend configuration
│
└── README.md
```

## 🎨 UI Features

- **Glassmorphism Design** - Modern frosted glass effects
- **Dark Theme** - Easy on the eyes with vibrant accents
- **Gradient Animations** - Smooth, eye-catching transitions
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Real-time Feedback** - Live status updates and progress indicators

## ⚙️ Configuration

### Backend (.env)

```env
HOST=0.0.0.0
PORT=8000
USE_GPU=False              # Set to True if you have CUDA GPU
CORS_ORIGINS=http://localhost:5173
MAX_AUDIO_LENGTH=60
SAMPLE_RATE=22050
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
```

## 🔧 API Endpoints

- `POST /upload-voice` - Upload voice sample and create model
- `POST /synthesize` - Synthesize speech from text
- `GET /models` - Get all voice models
- `GET /models/{model_id}` - Get specific model
- `PUT /models/{model_id}` - Update model info
- `DELETE /models/{model_id}` - Delete model
- `GET /audio/{filename}` - Serve audio file
- `GET /health` - Health check
- `GET /tts/info` - TTS engine information

## ⚠️ Ethical Use Guidelines

Voice cloning technology is powerful and should be used responsibly:

- ✅ **DO** use it for personal projects and creative content
- ✅ **DO** get explicit consent before cloning someone else's voice
- ✅ **DO** disclose when content is AI-generated
- ❌ **DON'T** use it to impersonate others without permission
- ❌ **DON'T** create misleading or harmful content
- ❌ **DON'T** violate privacy or intellectual property rights

## 🐛 Troubleshooting

### Backend Issues

**Error: "Could not load TTS model"**
- Ensure you have enough disk space (models are ~1-2GB)
- Check your internet connection for initial model download
- Try using CPU mode if GPU fails

**Error: "Audio quality validation failed"**
- Record in a quiet environment
- Speak clearly and at normal volume
- Ensure recording is at least 10 seconds

### Frontend Issues

**Error: "Network Error"**
- Ensure backend is running on port 8000
- Check CORS settings in backend `.env`
- Verify `VITE_API_URL` in frontend `.env`

**Audio not playing**
- Check browser console for errors
- Ensure browser supports Web Audio API
- Try a different browser (Chrome/Firefox recommended)

## 📝 License

This project is for educational and personal use. Please respect the licenses of the underlying technologies:
- Coqui TTS: Mozilla Public License 2.0
- React: MIT License
- FastAPI: MIT License

## 🙏 Acknowledgments

- **Coqui TTS** - For the amazing open-source TTS engine
- **WaveSurfer.js** - For beautiful audio visualization
- **Framer Motion** - For smooth animations

## 📧 Support

For issues, questions, or suggestions, please open an issue on GitHub.

---

**Built with ❤️ using cutting-edge AI technology**

© 2026 VoiceClone Studio | Powered by Coqui TTS
