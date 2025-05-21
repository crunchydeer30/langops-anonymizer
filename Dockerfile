FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m spacy download en_core_web_lg && \
    python -m spacy download ru_core_news_sm && \
    python -m spacy download xx_ent_wiki_sm

# Copy application code
COPY app/ ./app/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    APP_NAME="LangOps NER API" \
    ENVIRONMENT=production \
    LOG_LEVEL=INFO

# Expose the application port
EXPOSE 8000

# Run the application with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
