# exporters/diameter/app.py
from flask import Flask, Response
import prometheus_client
from prometheus_client import Counter, Gauge, Histogram
import random
import time
import threading
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('diameter-exporter')

# Configuration from environment variables
LISTEN_PORT = int(os.environ.get('DIAMETER_LISTEN_PORT', 9111))
SIMULATION_ENABLED = os.environ.get('DIAMETER_SIMULATION_ENABLED', 'true').lower() == 'true'
SIMULATION_INTERVAL = int(os.environ.get('DIAMETER_SIMULATION_INTERVAL', 5))

# Initialize Flask app
app = Flask(__name__)

# Initialize Prometheus metrics
# Request metrics
diameter_requests = Counter('telecom_diameter_requests_total', 'Total Diameter requests', ['type', 'origin_host'])
diameter_responses = Counter('telecom_diameter_responses_total', 'Total Diameter responses', ['type', 'result_code'])
diameter_timeouts = Counter('telecom_diameter_timeouts_total', 'Total Diameter timeouts', ['type'])

# Latency metrics
diameter_latency = Histogram('telecom_diameter_latency_seconds', 'Diameter request latency in seconds', 
                            ['type'], buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10])

# Error metrics
diameter_errors = Counter('telecom_diameter_errors_total', 'Diameter protocol errors', ['error_type', 'origin_host'])

# Session metrics
diameter_active_sessions = Gauge('telecom_diameter_active_sessions', 'Active Diameter sessions', ['type'])
diameter_session_duration = Histogram('telecom_diameter_session_duration_seconds', 'Diameter session duration in seconds',
                                    ['type'], buckets=[1, 5, 10, 30, 60, 300, 600, 1800, 3600, 7200, 14400])

# Transaction rate metrics
diameter_transactions_rate = Gauge('telecom_diameter_transactions_rate', 'Diameter transactions per second', ['type'])

@app.route('/metrics')
def metrics():
    """Endpoint to expose Prometheus metrics."""
    return Response(prometheus_client.generate_latest(), mimetype='text/plain')

@app.route('/health')
def health():
    """Health check endpoint."""
    return "Diameter Exporter is healthy"

def generate_diameter_metrics():
    """Generate simulated Diameter protocol metrics."""
    if not SIMULATION_ENABLED:
        logger.info("Simulation disabled, no metrics will be generated")
        return
    
    # Define common Diameter message types
    request_types = ['CCR', 'AAR', 'RAR', 'STR', 'ASR', 'DWR', 'DPR', 'ULR', 'AIR']
    result_codes = [2001, 2002, 2003, 3001, 3002, 3003, 4001, 4002, 4003, 5001, 5002, 5003]
    error_types = ['TIMEOUT', 'AUTHENTICATION_FAILED', 'UNKNOWN_SESSION', 'NETWORK_ERROR', 'PROTOCOL_ERROR']
    origin_hosts = ['mme01.example.com', 'pcrf02.example.com', 'hss03.example.com', 'dra01.example.com']
    
    # Initialize session counts
    for req_type in request_types:
        diameter_active_sessions.labels(type=req_type).set(random.randint(10, 1000))
    
    logger.info("Starting Diameter metrics simulation")
    
    while True:
        try:
            # Simulate request and response activity
            for _ in range(random.randint(5, 20)):
                req_type = random.choice(request_types)
                origin_host = random.choice(origin_hosts)
                
                # Generate a request
                diameter_requests.labels(type=req_type, origin_host=origin_host).inc()
                
                # Simulate latency
                latency = random.uniform(0.001, 0.5)  # Between 1ms and 500ms
                diameter_latency.labels(type=req_type).observe(latency)
                
                # Simulate errors (less frequent)
                if random.random() < 0.1:  # 10% error rate
                    error_type = random.choice(error_types)
                    diameter_errors.labels(error_type=error_type, origin_host=origin_host).inc()
                    # No response for errors
                else:
                    # Generate a response
                    result_code = random.choice(result_codes)
                    diameter_responses.labels(type=req_type, result_code=str(result_code)).inc()
                
            # Update session counts (some added, some removed)
            for req_type in request_types:
                current = diameter_active_sessions.labels(type=req_type)._value.get()
                if current is None:
                    current = random.randint(10, 1000)
                
                # Random change in session count
                change = random.randint(-50, 50)
                new_count = max(0, current + change)
                diameter_active_sessions.labels(type=req_type).set(new_count)
                
                # Record some session durations for completed sessions
                if change < 0:
                    for _ in range(abs(change)):
                        duration = random.uniform(10, 7200)  # 10s to 2 hours
                        diameter_session_duration.labels(type=req_type).observe(duration)
            
            # Update transaction rates
            for req_type in request_types:
                tps = random.uniform(5, 200)
                diameter_transactions_rate.labels(type=req_type).set(tps)
            
            logger.debug("Generated Diameter metrics")
            time.sleep(SIMULATION_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error generating Diameter metrics: {e}")
            time.sleep(10)  # Longer sleep on error

if __name__ == '__main__':
    # Start metrics generation in a separate thread
    if SIMULATION_ENABLED:
        simulation_thread = threading.Thread(target=generate_diameter_metrics, daemon=True)
        simulation_thread.start()
        logger.info(f"Diameter metrics simulation started with interval of {SIMULATION_INTERVAL}s")
    
    # Start the Flask server
    logger.info(f"Starting Diameter exporter on port {LISTEN_PORT}")
    app.run(host='0.0.0.0', port=LISTEN_PORT)
