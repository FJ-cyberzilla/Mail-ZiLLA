# Cyberzilla Enterprise Dockerfile
FROM python:3.11-slim

# Security: Run as non-root user
RUN groupadd -r cyberzilla && useradd -r -g cyberzilla cyberzilla

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p logs data proxies backups cache \
    && chown -R cyberzilla:cyberzilla /app

# Security: Switch to non-root user
USER cyberzilla

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 8000 5555

# Default command (override in docker-compose)
CMD ["python", "cli.py"]
