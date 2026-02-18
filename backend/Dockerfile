# Use official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for audio processing
# libsndfile1 is required by soundfile/librosa
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create directories for uploads and outputs if they don't exist
RUN mkdir -path uploads outputs models

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "main.py"]
