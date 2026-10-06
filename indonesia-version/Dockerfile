FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080

WORKDIR /app

# Install system utilities (curl for health checking)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy scenario modules, source documents, shared metadata, and unified portal
COPY 01-vector-search-1.0 /app/01-vector-search-1.0
COPY 02-agent-retrieval /app/02-agent-retrieval
COPY 03-rag-engine /app/03-rag-engine
COPY 04-agent-search-api /app/04-agent-search-api
COPY 05-agent-search-adk /app/05-agent-search-adk
COPY source-documents /app/source-documents
COPY source-documents-en /app/source-documents-en
COPY shared_corpus_metadata.py /app/shared_corpus_metadata.py
COPY unified-portal /app/unified-portal

# Navigate to portal directory where server.py is located
WORKDIR /app/unified-portal

EXPOSE 8080

CMD ["python", "server.py"]
