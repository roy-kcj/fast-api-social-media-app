FROM python:3.13-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1

# Prevents Python from buffering stdout/stderr (see logs immediately)
ENV PYTHONUNBUFFERED=1

# Working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn

# Copy application code
COPY . .

EXPOSE 8000

# Default command
# --host 0.0.0.0: Accept connections from outside the container
# --port 8000: Match the EXPOSE above
# Note: For development with hot reload, docker-compose.yml overrides this
CMD ["gunicorn", "src.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]