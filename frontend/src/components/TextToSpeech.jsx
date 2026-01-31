import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaPlay, FaPause, FaDownload, FaVolumeUp } from 'react-icons/fa';
import WaveSurfer from 'wavesurfer.js';
import { synthesizeSpeech, getAudioUrl } from '../api';
import './TextToSpeech.css';

const TextToSpeech = ({ selectedModel }) => {
    const [text, setText] = useState('');
    const [synthesizing, setSynthesizing] = useState(false);
    const [audioUrl, setAudioUrl] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [status, setStatus] = useState(null);
    const [language, setLanguage] = useState('en');

    const waveformRef = useRef(null);
    const wavesurferRef = useRef(null);

    useEffect(() => {
        return () => {
            if (wavesurferRef.current) {
                wavesurferRef.current.destroy();
            }
        };
    }, []);

    const handleSynthesize = async () => {
        if (!text.trim()) {
            setStatus({ type: 'error', message: 'Please enter some text' });
            return;
        }

        if (text.length > 1000) {
            setStatus({ type: 'error', message: 'Text is too long (max 1000 characters)' });
            return;
        }

        setSynthesizing(true);
        setStatus({ type: 'info', message: 'Synthesizing speech...' });

        try {
            const result = await synthesizeSpeech(text, selectedModel, language);

            if (result.success) {
                const fullAudioUrl = getAudioUrl(result.audio_url.split('/').pop());
                setAudioUrl(fullAudioUrl);
                createWaveform(fullAudioUrl);
                setStatus({ type: 'success', message: 'Speech synthesized successfully!' });
            } else {
                setStatus({ type: 'error', message: result.error || 'Synthesis failed' });
            }
        } catch (error) {
            console.error('Synthesis error:', error);
            setStatus({
                type: 'error',
                message: error.response?.data?.detail || 'Failed to synthesize speech. Please try again.'
            });
        } finally {
            setSynthesizing(false);
        }
    };

    const createWaveform = (url) => {
        if (wavesurferRef.current) {
            wavesurferRef.current.destroy();
        }

        const wavesurfer = WaveSurfer.create({
            container: waveformRef.current,
            waveColor: '#14b8a6',
            progressColor: '#06b6d4',
            cursorColor: '#f59e0b',
            barWidth: 2,
            barRadius: 3,
            height: 100,
            responsive: true,
        });

        wavesurfer.load(url);

        wavesurfer.on('finish', () => {
            setIsPlaying(false);
        });

        wavesurferRef.current = wavesurfer;
    };

    const togglePlayback = () => {
        if (wavesurferRef.current) {
            wavesurferRef.current.playPause();
            setIsPlaying(!isPlaying);
        }
    };

    const handleDownload = () => {
        if (audioUrl) {
            const a = document.createElement('a');
            a.href = audioUrl;
            a.download = 'synthesized_speech.wav';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        }
    };

    const exampleTexts = [
        "Hello! This is my cloned voice speaking. How amazing is that?",
        "The future of voice technology is here, and it's incredible.",
        "I can now make any text sound like me with just a few clicks."
    ];

    const useExample = (example) => {
        setText(example);
    };

    return (
        <motion.div
            className="text-to-speech glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="tts-header">
                <h3>Text to Speech Synthesis</h3>
                <p>
                    {selectedModel
                        ? 'Using your selected voice model'
                        : 'Select a voice model from the library above'}
                </p>
            </div>

            <div className="tts-content">
                <div className="text-input-section">
                    <div className="input-header">
                        <label htmlFor="text-input">Enter Text</label>
                        <span className="char-counter">
                            {text.length} / 1000
                        </span>
                    </div>

                    <textarea
                        id="text-input"
                        className="input-field text-area"
                        placeholder="Type or paste the text you want to synthesize..."
                        value={text}
                        onChange={(e) => setText(e.target.value)}
                        rows={6}
                        maxLength={1000}
                    />

                    <div className="examples-section">
                        <p className="examples-label">Try an example:</p>
                        <div className="examples-buttons">
                            {exampleTexts.map((example, index) => (
                                <button
                                    key={index}
                                    className="btn btn-secondary btn-sm"
                                    onClick={() => useExample(example)}
                                >
                                    Example {index + 1}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="language-selector">
                        <label htmlFor="language">Language:</label>
                        <select
                            id="language"
                            className="input-field"
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                        >
                            <option value="en">English</option>
                            <option value="es">Spanish</option>
                            <option value="fr">French</option>
                            <option value="de">German</option>
                            <option value="it">Italian</option>
                            <option value="pt">Portuguese</option>
                        </select>
                    </div>

                    <button
                        className="btn btn-primary synthesize-btn"
                        onClick={handleSynthesize}
                        disabled={synthesizing || !text.trim()}
                    >
                        {synthesizing ? (
                            <>
                                <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
                                Synthesizing...
                            </>
                        ) : (
                            <>
                                <FaVolumeUp /> Synthesize Speech
                            </>
                        )}
                    </button>
                </div>

                {status && (
                    <motion.div
                        className={`status-badge ${status.type}`}
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        {status.message}
                    </motion.div>
                )}

                {audioUrl && (
                    <motion.div
                        className="audio-player-section"
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        transition={{ duration: 0.3 }}
                    >
                        <h4>Generated Audio</h4>

                        <div className="waveform-container">
                            <div ref={waveformRef} className="waveform"></div>
                        </div>

                        <div className="audio-controls">
                            <button className="btn btn-secondary" onClick={togglePlayback}>
                                {isPlaying ? <FaPause /> : <FaPlay />}
                                {isPlaying ? 'Pause' : 'Play'}
                            </button>
                            <button className="btn btn-success" onClick={handleDownload}>
                                <FaDownload /> Download
                            </button>
                        </div>
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
};

export default TextToSpeech;
