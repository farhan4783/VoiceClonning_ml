import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FaMicrophone, FaStop, FaPlay, FaPause, FaUpload, FaTrash } from 'react-icons/fa';
import WaveSurfer from 'wavesurfer.js';
import { uploadVoice } from '../api';
import './VoiceRecorder.css';

const VoiceRecorder = ({ onVoiceUploaded }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isPaused, setIsPaused] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const [audioBlob, setAudioBlob] = useState(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [uploading, setUploading] = useState(false);
    const [uploadStatus, setUploadStatus] = useState(null);
    const [modelName, setModelName] = useState('');
    const [description, setDescription] = useState('');

    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const timerRef = useRef(null);
    const waveformRef = useRef(null);
    const wavesurferRef = useRef(null);

    useEffect(() => {
        return () => {
            if (timerRef.current) clearInterval(timerRef.current);
            if (wavesurferRef.current) wavesurferRef.current.destroy();
        };
    }, []);

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorder.onstop = () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/wav' });
                setAudioBlob(blob);
                createWaveform(blob);
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);

            timerRef.current = setInterval(() => {
                setRecordingTime(prev => prev + 1);
            }, 1000);
        } catch (error) {
            console.error('Error accessing microphone:', error);
            alert('Could not access microphone. Please check permissions.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            setIsPaused(false);
            if (timerRef.current) {
                clearInterval(timerRef.current);
            }
        }
    };

    const pauseRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            if (isPaused) {
                mediaRecorderRef.current.resume();
                timerRef.current = setInterval(() => {
                    setRecordingTime(prev => prev + 1);
                }, 1000);
            } else {
                mediaRecorderRef.current.pause();
                if (timerRef.current) {
                    clearInterval(timerRef.current);
                }
            }
            setIsPaused(!isPaused);
        }
    };

    const createWaveform = (blob) => {
        if (wavesurferRef.current) {
            wavesurferRef.current.destroy();
        }

        const wavesurfer = WaveSurfer.create({
            container: waveformRef.current,
            waveColor: '#6366f1',
            progressColor: '#8b5cf6',
            cursorColor: '#ec4899',
            barWidth: 2,
            barRadius: 3,
            height: 80,
            responsive: true,
        });

        wavesurfer.loadBlob(blob);

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

    const deleteRecording = () => {
        setAudioBlob(null);
        setRecordingTime(0);
        setIsPlaying(false);
        setUploadStatus(null);
        if (wavesurferRef.current) {
            wavesurferRef.current.destroy();
        }
    };

    const handleUpload = async () => {
        if (!audioBlob || !modelName.trim()) {
            alert('Please provide a name for your voice model');
            return;
        }

        if (recordingTime < 10) {
            alert('Recording is too short. Please record at least 10 seconds.');
            return;
        }

        setUploading(true);
        setUploadStatus(null);

        try {
            const audioFile = new File([audioBlob], `${modelName}.wav`, { type: 'audio/wav' });
            const result = await uploadVoice(audioFile, modelName, description);

            if (result.success) {
                setUploadStatus({ type: 'success', message: 'Voice model created successfully!' });
                setModelName('');
                setDescription('');
                deleteRecording();
                if (onVoiceUploaded) onVoiceUploaded();
            } else {
                setUploadStatus({ type: 'error', message: result.error || 'Upload failed' });
            }
        } catch (error) {
            console.error('Upload error:', error);
            setUploadStatus({
                type: 'error',
                message: error.response?.data?.detail || 'Failed to upload voice. Please try again.'
            });
        } finally {
            setUploading(false);
        }
    };

    const formatTime = (seconds) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, '0')}`;
    };

    return (
        <motion.div
            className="voice-recorder glass-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="recorder-header">
                <h3>Voice Recording Studio</h3>
                <p>Record at least 30 seconds for best results</p>
            </div>

            <div className="recorder-controls">
                {!isRecording && !audioBlob && (
                    <motion.button
                        className="btn btn-primary record-btn"
                        onClick={startRecording}
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                    >
                        <FaMicrophone /> Start Recording
                    </motion.button>
                )}

                {isRecording && (
                    <div className="recording-active">
                        <div className="recording-indicator">
                            <span className="pulse-dot"></span>
                            <span className="recording-time">{formatTime(recordingTime)}</span>
                        </div>

                        <div className="recording-buttons">
                            <button className="btn btn-secondary" onClick={pauseRecording}>
                                {isPaused ? <FaPlay /> : <FaPause />}
                                {isPaused ? 'Resume' : 'Pause'}
                            </button>
                            <button className="btn btn-primary" onClick={stopRecording}>
                                <FaStop /> Stop
                            </button>
                        </div>
                    </div>
                )}

                {audioBlob && (
                    <div className="playback-section">
                        <div className="waveform-container">
                            <div ref={waveformRef} className="waveform"></div>
                        </div>

                        <div className="playback-controls">
                            <button className="btn btn-secondary" onClick={togglePlayback}>
                                {isPlaying ? <FaPause /> : <FaPlay />}
                                {isPlaying ? 'Pause' : 'Play'}
                            </button>
                            <span className="duration">{formatTime(recordingTime)}</span>
                            <button className="btn btn-secondary" onClick={deleteRecording}>
                                <FaTrash /> Delete
                            </button>
                        </div>

                        <div className="upload-form">
                            <input
                                type="text"
                                className="input-field"
                                placeholder="Voice model name (e.g., My Voice)"
                                value={modelName}
                                onChange={(e) => setModelName(e.target.value)}
                            />
                            <textarea
                                className="input-field"
                                placeholder="Description (optional)"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                rows={2}
                            />
                            <button
                                className="btn btn-success"
                                onClick={handleUpload}
                                disabled={uploading || !modelName.trim()}
                            >
                                {uploading ? (
                                    <>
                                        <div className="spinner" style={{ width: '20px', height: '20px' }}></div>
                                        Uploading...
                                    </>
                                ) : (
                                    <>
                                        <FaUpload /> Create Voice Model
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {uploadStatus && (
                <motion.div
                    className={`status-badge ${uploadStatus.type}`}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ marginTop: '1rem' }}
                >
                    {uploadStatus.message}
                </motion.div>
            )}
        </motion.div>
    );
};

export default VoiceRecorder;
