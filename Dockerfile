
FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    poppler-utils \
    build-essential \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --upgrade pip
RUN pip install gradio pdf2image pillow numpy

EXPOSE 7860
CMD ["python", "brevet_gradio_app.py"]
