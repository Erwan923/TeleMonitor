# exporters/ipsec/Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask prometheus_client

# Copy application
COPY app.py /app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$IPSEC_LISTEN_PORT/health || exit 1

# Expose the port
EXPOSE 8079

# Default environment variables
ENV IPSEC_LISTEN_PORT=8079
ENV IPSEC_SIMULATION_ENABLED=true
ENV IPSEC_SIMULATION_INTERVAL=5

# Run the application
CMD ["python", "app.py"]
