# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py \
    FLASK_ENV=production \
    PYTHONPATH=/app \
    PORT=5001 \
    METRICS_PORT=9101 \
    LOG_LEVEL=INFO

# Required environment variables (will be overridden at runtime)
ENV STRIPE_SECRET_KEY="" \
    STRIPE_WEBHOOK_SECRET="" \
    EVENT_SERVICE_URL="http://event-service:5000"

# Install system dependencies including curl for healthcheck
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pip build tools to avoid bdist_wheel errors
RUN pip install --upgrade pip wheel setuptools


# Copy the dependencies file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files into the Docker image
COPY . .

# Create non-root user for security
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose application port and Prometheus metrics port
EXPOSE 9101

# Run the application with Gunicorn with improved configuration
CMD ["gunicorn", \
    #  "--bind", "0.0.0.0:5001", \
     "--workers", "4", \
     "--threads", "2", \
     "--worker-class", "gthread", \
     "--worker-tmp-dir", "/dev/shm", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "app:app"]