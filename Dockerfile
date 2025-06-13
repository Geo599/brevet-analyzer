FROM python:3.10-slim

# Install system-level dependencies for image and PDF handling
RUN apt-get update && apt-get install -y \
    poppler-utils \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all app files into the container
COPY . /app

# Install Python dependencies including PyMuPDF for symbol detection
RUN pip install --upgrade pip
RUN pip install gradio pdf2image pillow numpy pymupdf

# Expose Gradio's default port
EXPOSE 7860

# Launch the hybrid app
CMD ["python", "brevet_gradio_app_hybrid.py"]
