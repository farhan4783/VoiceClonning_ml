import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FaUser, FaRobot, FaTrash, FaEdit, FaCheck, FaTimes } from 'react-icons/fa';
import { getModels, deleteModel, updateModel } from '../api';
import './VoiceLibrary.css';

const VoiceLibrary = ({ refreshTrigger, onModelSelect, selectedModel }) => {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [editingId, setEditingId] = useState(null);
    const [editName, setEditName] = useState('');
    const [editDescription, setEditDescription] = useState('');

    useEffect(() => {
        fetchModels();
    }, [refreshTrigger]);

    const fetchModels = async () => {
        setLoading(true);
        try {
            const response = await getModels();
            if (response.success) {
                setModels(response.models);
            }
        } catch (error) {
            console.error('Error fetching models:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (modelId) => {
        if (!confirm('Are you sure you want to delete this voice model?')) {
            return;
        }

        try {
            const result = await deleteModel(modelId);
            if (result.success) {
                setModels(models.filter(m => m.id !== modelId));
                if (selectedModel === modelId) {
                    onModelSelect(null);
                }
            }
        } catch (error) {
            console.error('Error deleting model:', error);
            alert('Failed to delete model');
        }
    };

    const startEdit = (model) => {
        setEditingId(model.id);
        setEditName(model.name);
        setEditDescription(model.description || '');
    };

    const cancelEdit = () => {
        setEditingId(null);
        setEditName('');
        setEditDescription('');
    };

    const saveEdit = async (modelId) => {
        try {
            const result = await updateModel(modelId, editName, editDescription);
            if (result.success) {
                setModels(models.map(m => m.id === modelId ? result.model_info : m));
                cancelEdit();
            }
        } catch (error) {
            console.error('Error updating model:', error);
            alert('Failed to update model');
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'Unknown';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    };

    if (loading) {
        return (
            <div className="voice-library-loading">
                <div className="spinner"></div>
                <p>Loading voice models...</p>
            </div>
        );
    }

    if (models.length === 0) {
        return (
            <motion.div
                className="voice-library-empty glass-card"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                <FaRobot size={64} style={{ opacity: 0.3, marginBottom: '1rem' }} />
                <h3>No Voice Models Yet</h3>
                <p>Record your first voice sample above to get started!</p>
            </motion.div>
        );
    }

    return (
        <div className="voice-library">
            <div className="models-grid">
                <AnimatePresence>
                    {models.map((model, index) => (
                        <motion.div
                            key={model.id}
                            className={`model-card glass-card ${selectedModel === model.id ? 'selected' : ''}`}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.9 }}
                            transition={{ delay: index * 0.1 }}
                            onClick={() => !editingId && onModelSelect(model.id)}
                        >
                            <div className="model-icon">
                                {model.type === 'preset' ? <FaRobot /> : <FaUser />}
                            </div>

                            {editingId === model.id ? (
                                <div className="model-edit-form" onClick={(e) => e.stopPropagation()}>
                                    <input
                                        type="text"
                                        className="input-field"
                                        value={editName}
                                        onChange={(e) => setEditName(e.target.value)}
                                        placeholder="Model name"
                                    />
                                    <textarea
                                        className="input-field"
                                        value={editDescription}
                                        onChange={(e) => setEditDescription(e.target.value)}
                                        placeholder="Description"
                                        rows={2}
                                    />
                                    <div className="edit-actions">
                                        <button className="btn btn-success btn-sm" onClick={() => saveEdit(model.id)}>
                                            <FaCheck /> Save
                                        </button>
                                        <button className="btn btn-secondary btn-sm" onClick={cancelEdit}>
                                            <FaTimes /> Cancel
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <>
                                    <div className="model-info">
                                        <h4>{model.name}</h4>
                                        {model.description && <p className="model-description">{model.description}</p>}
                                        <div className="model-meta">
                                            <span className="model-type">
                                                {model.type === 'preset' ? 'Preset' : 'Custom'}
                                            </span>
                                            <span className="model-date">{formatDate(model.created_at)}</span>
                                        </div>
                                        {model.duration && (
                                            <div className="model-stats">
                                                <span>Duration: {model.duration.toFixed(1)}s</span>
                                                {model.quality_metrics?.snr_db && (
                                                    <span>Quality: {model.quality_metrics.snr_db.toFixed(1)} dB</span>
                                                )}
                                            </div>
                                        )}
                                    </div>

                                    {model.type !== 'preset' && (
                                        <div className="model-actions" onClick={(e) => e.stopPropagation()}>
                                            <button
                                                className="btn-icon"
                                                onClick={() => startEdit(model)}
                                                title="Edit"
                                            >
                                                <FaEdit />
                                            </button>
                                            <button
                                                className="btn-icon danger"
                                                onClick={() => handleDelete(model.id)}
                                                title="Delete"
                                            >
                                                <FaTrash />
                                            </button>
                                        </div>
                                    )}
                                </>
                            )}

                            {selectedModel === model.id && (
                                <div className="selected-badge">
                                    <FaCheck /> Selected
                                </div>
                            )}
                        </motion.div>
                    ))}
                </AnimatePresence>
            </div>
        </div>
    );
};

export default VoiceLibrary;
