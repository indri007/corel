FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential curl git \
        tesseract-ocr tesseract-ocr-ind \
        poppler-utils potrace \
        libreoffice --no-install-recommends \
        fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8501
HEALTHCHECK CMD curl -fsS http://localhost:8501/_stcore/health || exit 1
CMD ["streamlit", "run", "app.py", "--server.headless=true", "--server.port=8501", "--server.address=0.0.0.0"]
