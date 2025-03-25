# exporters/diameter/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask prometheus_client

# Copy application
COPY app.py /app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$DIAMETER_LISTEN_PORT/health || exit 1

# Expose the port
EXPOSE 9111

# Default environment variables
ENV DIAMETER_LISTEN_PORT=9111
ENV DIAMETER_SIMULATION_ENABLED=true
ENV DIAMETER_SIMULATION_INTERVAL=5

# Run the application
CMD ["python", "app.py"]
