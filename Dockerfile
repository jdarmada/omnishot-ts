# Stage 1: build the TypeScript frontend
FROM node:22-slim AS frontend
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python runtime serving API + built frontend
FROM python:3.12-slim

# ffmpeg for chunking/proxies; libgl/libglib for opencv (scenedetect)
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend/ backend/
COPY --from=frontend /build/dist frontend/dist

ENV WATCH_DIR=/data/clips \
    CHUNKS_DIR=/data/chunks

EXPOSE 8001
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8001"]
