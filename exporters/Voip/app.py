# exporters/voip/app.py
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
logger = logging.getLogger('voip-exporter')

# Configuration from environment variables
LISTEN_PORT = int(os.environ.get('VOIP_LISTEN_PORT', 9010))
SIMULATION_ENABLED = os.environ.get('VOIP_SIMULATION_ENABLED', 'true').lower() == 'true'
SIMULATION_INTERVAL = int(os.environ.get('VOIP_SIMULATION_INTERVAL', 5))

# Initialize Flask app
app = Flask(__name__)

# Initialize Prometheus metrics

# Active calls metrics
voip_active_calls = Gauge('telecom_voip_active_calls', 'Currently active VoIP calls')
voip_active_calls_by_codec = Gauge('telecom_voip_active_calls_by_codec', 'Currently active VoIP calls by codec', ['codec'])
voip_active_calls_by_region = Gauge('telecom_voip_active_calls_by_region', 'Currently active VoIP calls by region', ['region'])

# Call quality metrics
voip_mos = Gauge('telecom_voip_mos', 'Mean Opinion Score (MOS) for VoIP quality (1-5)', ['codec'])
voip_jitter = Gauge('telecom_voip_jitter_ms', 'VoIP jitter in milliseconds', ['codec'])
voip_packet_loss = Gauge('telecom_voip_packet_loss_percent', 'VoIP packet loss percentage', ['codec'])
voip_latency = Gauge('telecom_voip_latency_ms', 'VoIP one-way latency in milliseconds', ['codec'])
voip_r_factor = Gauge('telecom_voip_r_factor', 'R-Factor quality metric (0-100)', ['codec'])

# Call statistics
voip_calls_total = Counter('telecom_voip_calls_total', 'Total VoIP calls', ['codec', 'result'])
voip_call_duration = Histogram('telecom_voip_call_duration_seconds', 'VoIP call duration in seconds', 
                               ['codec'], buckets=[10, 30, 60, 120, 300, 600, 1200, 1800, 3600, 7200])

# SIP metrics
voip_sip_transactions = Counter('telecom_voip_sip_transactions_total', 'Total SIP transactions', ['method'])
voip_sip_errors = Counter('telecom_voip_sip_errors_total', 'SIP transaction errors', ['code', 'method'])

@app.route('/metrics')
def metrics():
    """Endpoint to expose Prometheus metrics."""
    return Response(prometheus_client.generate_latest(), mimetype='text/plain')

@app.route('/health')
def health():
    """Health check endpoint."""
    return "VoIP Exporter is healthy"

def generate_voip_metrics():
    """Generate simulated VoIP metrics."""
    if not SIMULATION_ENABLED:
        logger.info("Simulation disabled, no metrics will be generated")
        return
    
    # Define common VoIP codecs and regions
    codecs = ['G.711', 'G.729', 'Opus', 'AMR-WB', 'EVS']
    regions = ['north', 'south', 'east', 'west', 'central']
    sip_methods = ['INVITE', 'BYE', 'REGISTER', 'CANCEL', 'OPTIONS', 'UPDATE', 'REFER']
    sip_error_codes = ['400', '403', '404', '408', '480', '486', '487', '500', '503', '504']
    call_results = ['completed', 'failed', 'busy', 'no_answer', 'rejected']
    
    # Initialize call counts with random values
    total_calls = random.randint(50, 500)
    voip_active_calls.set(total_calls)
    
    # Distribute calls among codecs and regions
    for codec in codecs:
        codec_calls = random.randint(10, 100)
        voip_active_calls_by_codec.labels(codec=codec).set(codec_calls)
        
        # Initialize quality metrics
        voip_mos.labels(codec=codec).set(random.uniform(3.0, 4.8))
        voip_jitter.labels(codec=codec).set(random.uniform(5, 60))
        voip_packet_loss.labels(codec=codec).set(random.uniform(0, 5))
        voip_latency.labels(codec=codec).set(random.uniform(20, 200))
        voip_r_factor.labels(codec=codec).set(random.uniform(70, 93))
    
    for region in regions:
        voip_active_calls_by_region.labels(region=region).set(random.randint(10, 100))
    
    logger.info("Starting VoIP metrics simulation")
    
    while True:
        try:
            # Simulate call activity
            
            # Update active calls (with a trend)
            current_calls = voip_active_calls._value.get() or 0
            trend = random.uniform(-30, 30)  # Trend up or down
            new_calls = max(0, min(1000, current_calls + trend))  # Limit between 0 and 1000
            voip_active_calls.set(new_calls)
            
            # Update codec-specific metrics
            for codec in codecs:
                # Update active calls by codec
                current_codec_calls = voip_active_calls_by_codec.labels(codec=codec)._value.get() or 0
                codec_trend = random.uniform(-10, 10)
                new_codec_calls = max(0, min(200, current_codec_calls + codec_trend))
                voip_active_calls_by_codec.labels(codec=codec).set(new_codec_calls)
                
                # Update quality metrics with slight variations
                current_mos = voip_mos.labels(codec=codec)._value.get() or 4.0
                mos_change = random.uniform(-0.2, 0.2)
                new_mos = max(1.0, min(5.0, current_mos + mos_change))
                voip_mos.labels(codec=codec).set(new_mos)
                
                current_jitter = voip_jitter.labels(codec=codec)._value.get() or 20
                jitter_change = random.uniform(-5, 5)
                new_jitter = max(0, current_jitter + jitter_change)
                voip_jitter.labels(codec=codec).set(new_jitter)
                
                current_loss = voip_packet_loss.labels(codec=codec)._value.get() or 1.0
                loss_change = random.uniform(-0.5, 0.5)
                new_loss = max(0, min(100, current_loss + loss_change))
                voip_packet_loss.labels(codec=codec).set(new_loss)
                
                current_latency = voip_latency.labels(codec=codec)._value.get() or 100
                latency_change = random.uniform(-10, 10)
                new_latency = max(10, current_latency + latency_change)
                voip_latency.labels(codec=codec).set(new_latency)
                
                current_rfactor = voip_r_factor.labels(codec=codec)._value.get() or 80
                rfactor_change = random.uniform(-2, 2)
                new_rfactor = max(0, min(100, current_rfactor + rfactor_change))
                voip_r_factor.labels(codec=codec).set(new_rfactor)
                
                # Register completed calls
                completed_calls = random.randint(1, 10)
                for result in call_results:
                    count = random.randint(0, 3)
                    voip_calls_total.labels(codec=codec, result=result).inc(count)
                    
                    # For completed calls, record duration
                    if result == 'completed':
                        for _ in range(count):
                            duration = random.uniform(30, 3600)  # 30s to 1h
                            voip_call_duration.labels(codec=codec).observe(duration)
            
            # Update region distribution
            for region in regions:
                current_region_calls = voip_active_calls_by_region.labels(region=region)._value.get() or 50
                region_trend = random.uniform(-5, 5)
                new_region_calls = max(0, min(200, current_region_calls + region_trend))
                voip_active_calls_by_region.labels(region=region).set(new_region_calls)
            
            # Generate SIP transaction metrics
            for method in sip_methods:
                # Normal transactions
                transaction_count = random.randint(5, 50)
                voip_sip_transactions.labels(method=method).inc(transaction_count)
                
                # Error transactions
                if random.random() < 0.2:  # 20% chance of errors
                    error_code = random.choice(sip_error_codes)
                    error_count = random.randint(1, 5)
                    voip_sip_errors.labels(code=error_code, method=method).inc(error_count)
            
            logger.debug("Generated VoIP metrics")
            time.sleep(SIMULATION_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error generating VoIP metrics: {e}")
            time.sleep(10)  # Longer sleep on error

if __name__ == '__main__':
    # Start metrics generation in a separate thread
    if SIMULATION_ENABLED:
        simulation_thread = threading.Thread(target=generate_voip_metrics, daemon=True)
        simulation_thread.start()
        logger.info(f"VoIP metrics simulation started with interval of {SIMULATION_INTERVAL}s")
    
    # Start the Flask server
    logger.info(f"Starting VoIP exporter on port {LISTEN_PORT}")
    app.run(host='0.0.0.0', port=LISTEN_PORT)
