# Use Python 3.11 slim image
FROM python:3.11-slim

# Build argument for cache busting
ARG BUILD_DATE

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY view_logs.py .
COPY questions.txt .

# Create logs directory with proper permissions
RUN mkdir -p /app/logs && chmod 755 /app/logs

# Create non-root user for security
RUN useradd -m -u 1000 tutorai && \
    chown -R tutorai:tutorai /app

# Switch to non-root user
USER tutorai

# Expose port
EXPOSE 7777

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV GRADIO_SERVER_NAME=0.0.0.0
ENV GRADIO_SERVER_PORT=7777

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7777/ || exit 1

# Run the application
CMD ["python", "app.py", "--host", "0.0.0.0", "--port", "7777"]
