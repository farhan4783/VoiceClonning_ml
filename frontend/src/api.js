import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Response interceptor for error handling
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error('API Error:', error.response ? error.response.data : error.message);
        if (error.response) {
            // Server responded with a status code outside the 2xx range
            const message = error.response.data.detail || 'An unexpected error occurred';
            // You could trigger a toast notification here
            // toast.error(message);
            return Promise.reject(new Error(message));
        } else if (error.request) {
            // The request was made but no response was received
            return Promise.reject(new Error('No response from server. Please check your connection.'));
        } else {
            // Something happened in setting up the request
            return Promise.reject(error);
        }
    }
);

export const uploadVoice = async (audioFile, modelName, description = '') => {
    const formData = new FormData();
    formData.append('file', audioFile);
    formData.append('model_name', modelName);
    formData.append('description', description);

    const response = await api.post('/upload-voice', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });

    return response.data;
};

export const synthesizeSpeech = async (text, modelId = null, language = 'en') => {
    const response = await api.post('/synthesize', {
        text,
        model_id: modelId,
        language,
    });

    return response.data;
};

export const getModels = async () => {
    const response = await api.get('/models');
    return response.data;
};

export const getModel = async (modelId) => {
    const response = await api.get(`/models/${modelId}`);
    return response.data;
};

export const updateModel = async (modelId, name, description) => {
    const response = await api.put(`/models/${modelId}`, {
        name,
        description,
    });

    return response.data;
};

export const deleteModel = async (modelId) => {
    const response = await api.delete(`/models/${modelId}`);
    return response.data;
};

export const getAudioUrl = (filename) => {
    return `${API_BASE_URL}/audio/${filename}`;
};

export const getTTSInfo = async () => {
    const response = await api.get('/tts/info');
    return response.data;
};

export default api;
