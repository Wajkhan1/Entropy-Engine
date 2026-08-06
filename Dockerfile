FROM python:3.10-slim

# Label metadata
LABEL authors="Admin"

WORKDIR /app

# Install GCC, Python headers, and system dependencies for PyAudio and PyQt5
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    portaudio19-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
