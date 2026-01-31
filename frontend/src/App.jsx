import { useState } from 'react'
import './App.css'
import Hero from './components/Hero'
import VoiceRecorder from './components/VoiceRecorder'
import TextToSpeech from './components/TextToSpeech'
import VoiceLibrary from './components/VoiceLibrary'

function App() {
    const [selectedModel, setSelectedModel] = useState(null)
    const [refreshModels, setRefreshModels] = useState(0)

    const handleVoiceUploaded = () => {
        // Trigger refresh of voice library
        setRefreshModels(prev => prev + 1)
    }

    const handleModelSelect = (modelId) => {
        setSelectedModel(modelId)
        // Scroll to TTS section
        document.getElementById('tts-section')?.scrollIntoView({ behavior: 'smooth' })
    }

    return (
        <>
            <div className="animated-bg"></div>

            <div className="app-content">
                <Hero />

                <div className="container">
                    <section className="section">
                        <div className="section-header text-center mb-4">
                            <h2 className="gradient-text">Clone Your Voice</h2>
                            <p>Record 30 seconds of your voice to create a personalized AI voice model</p>
                        </div>
                        <VoiceRecorder onVoiceUploaded={handleVoiceUploaded} />
                    </section>

                    <section className="section">
                        <div className="section-header text-center mb-4">
                            <h2 className="gradient-text">Your Voice Library</h2>
                            <p>Manage your cloned voices and select one for synthesis</p>
                        </div>
                        <VoiceLibrary
                            refreshTrigger={refreshModels}
                            onModelSelect={handleModelSelect}
                            selectedModel={selectedModel}
                        />
                    </section>

                    <section className="section" id="tts-section">
                        <div className="section-header text-center mb-4">
                            <h2 className="gradient-text">Text to Speech</h2>
                            <p>Type any text and hear it in your cloned voice</p>
                        </div>
                        <TextToSpeech selectedModel={selectedModel} />
                    </section>
                </div>

                <footer style={{
                    textAlign: 'center',
                    padding: '3rem 0',
                    color: 'var(--text-tertiary)',
                    position: 'relative',
                    zIndex: 1
                }}>
                    <p>VoiceClone Studio © 2026 | Powered by Coqui TTS</p>
                </footer>
            </div>
        </>
    )
}

export default App
