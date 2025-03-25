# simulator/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask prometheus_client

# Create directory structure
RUN mkdir -p /app/templates /app/static /app/dashboards

# Copy application files
COPY app.py /app/
COPY templates /app/templates/
COPY static /app/static/
COPY dashboards /app/dashboards/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1

# Expose ports
EXPOSE 5000 8000

# Default environment variables
ENV SIMULATION_INTERVAL=5
ENV LOG_LEVEL=INFO

# Run the application
CMD ["python", "app.py"]
