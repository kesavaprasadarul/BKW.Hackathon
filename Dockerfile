FROM python:3.11-slim

# Prevent Python from writing .pyc files and ensure stdout/stderr are unbuffered
ENV PYTHONDONTWRITEBYTECODE=1 \
		PYTHONUNBUFFERED=1 \
		GOOGLE_GEMINI_API_KEY="" \
		GEMINI_API_KEY=""

# Set working directory to src inside /app
WORKDIR /app/src

# Install system dependencies (if any needed later). Keeping minimal for now.
RUN apt-get update && apt-get install -y --no-install-recommends \
		build-essential \
		&& rm -rf /var/lib/apt/lists/*

# Copy requirements (choose root requirements.txt; identical to src/requirements.txt) and install
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy full project (everything not ignored by .dockerignore/.gitignore). We copy root, then rely on WORKDIR
COPY . /app

# Expose FastAPI default port
EXPOSE 8000

# Healthcheck to ensure container is responsive
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
	CMD curl -f http://localhost:8000/health || exit 1

# Default command: run the API with uvicorn
CMD ["python", "api.py"]