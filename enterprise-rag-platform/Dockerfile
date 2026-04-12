# EKIP RAG API — deploy to Render, Fly.io, Koyeb, Railway, etc.
FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ekip ./ekip
COPY api ./api
COPY configs ./configs

# Optional: copy a pre-built index at image build time (see DEPLOY-FREE.md)
# COPY data/vectorstore ./data/vectorstore

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["sh", "-c", "uvicorn api.app:app --host 0.0.0.0 --port ${PORT:-8080}"]
