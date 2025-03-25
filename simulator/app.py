# simulator/app.py
from flask import Flask, render_template, jsonify, request
from prometheus_client import start_http_server, Gauge, Counter, Histogram
import threading
import time
import random
import logging
import os
import json

# Configuration from environment variables
SIMULATION_INTERVAL = int(os.environ.get('SIMULATION_INTERVAL', 5))
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()

# Configure logging
logging_level = getattr(logging, LOG_LEVEL)
logging.basicConfig(level=logging_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TeleMonitor')

# Initialize Flask
app = Flask(__name__)

# Prometheus metrics for telecommunications

# Diameter protocol metrics
diameter_requests = Counter('telecom_diameter_requests_total', 'Total Diameter requests', ['type'])
diameter_latency = Gauge('telecom_diameter_latency_ms', 'Diameter latency in ms', ['type'])
diameter_errors = Counter('telecom_diameter_errors_total', 'Diameter errors', ['error_type'])
diameter_active_sessions = Gauge('telecom_diameter_active_sessions', 'Active Diameter sessions', ['application'])

# VoIP metrics
voip_calls = Gauge('telecom_voip_active_calls', 'Active VoIP calls')
voip_quality = Gauge('telecom_voip_mos', 'Mean Opinion Score (1-5)', ['codec'])
voip_jitter = Gauge('telecom_voip_jitter_ms', 'VoIP jitter in ms', ['codec'])
voip_packet_loss = Gauge('telecom_voip_packet_loss_percent', 'VoIP packet loss percentage', ['codec'])
voip_call_setup_time = Histogram('telecom_voip_call_setup_time_ms', 'VoIP call setup time in ms', 
                                ['codec'], buckets=[50, 100, 200, 500, 1000, 2000, 5000])

# IPsec metrics
ipsec_tunnels = Gauge('telecom_ipsec_tunnels', 'IPsec tunnels by state', ['state'])
ipsec_bandwidth = Gauge('telecom_ipsec_bandwidth_mbps', 'IPsec bandwidth (Mbps)', ['tunnel_id'])
ipsec_latency = Gauge('telecom_ipsec_latency_ms', 'IPsec tunnel latency in ms', ['tunnel_id'])
ipsec_crypto_errors = Counter('telecom_ipsec_crypto_errors_total', 'IPsec cryptographic errors', ['error_type'])

# Mobile network metrics
mobile_subscribers = Gauge('telecom_mobile_subscribers', 'Mobile subscribers by type', ['type'])
mobile_data_traffic = Gauge('telecom_mobile_data_traffic_gbps', 'Mobile data traffic in Gbps', ['generation'])
mobile_signal_quality = Gauge('telecom_mobile_signal_quality', 'Mobile signal quality (0-100)', ['generation', 'cell_id'])
mobile_handovers = Counter('telecom_mobile_handovers_total', 'Mobile handover operations', ['result'])

# API data for history
metrics_history = {
    'timestamp': [],
    'diameter_requests': [],
    'voip_calls': [],
    'ipsec_tunnels': [],
    'mobile_subscribers': []
}

# Maximum history size
MAX_HISTORY_SIZE = 100

# Flask routes
@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for historical metrics."""
    return jsonify(metrics_history)

@app.route('/api/status')
def get_status():
    """API endpoint for component status."""
    components = {
        'simulator': {
            'status': 'active',
            'uptime': '00:00:00',  # Would be calculated in a real app
            'metrics_count': len(metrics_history['timestamp'])
        },
        'prometheus': {
            'status': 'active',
            'address': 'prometheus:9090'
        },
        'grafana': {
            'status': 'active',
            'address': 'grafana:3000'
        },
        'exporters': {
            'diameter': check_exporter_status('diameter-exporter', 9111),
            'voip': check_exporter_status('voip-exporter', 9010),
            'ipsec': check_exporter_status('ipsec-exporter', 8079)
        }
    }
    return jsonify(components)

@app.route('/api/control', methods=['POST'])
def control_simulator():
    """API endpoint to control simulation parameters."""
    data = request.json
    response = {'status': 'success', 'message': 'Settings updated'}
    
    try:
        # Example of parameter adjustment (in a real system, these would affect the simulator)
        if 'voip_call_rate' in data:
            # Would adjust call simulation rate
            response['message'] = f"VoIP call rate set to {data['voip_call_rate']}"
            
        if 'error_rate' in data:
            # Would adjust error simulation rate
            response['message'] = f"Error rate set to {data['error_rate']}%"
            
        if 'simulation_mode' in data:
            # Would switch simulation modes (normal, high-load, failure)
            response['message'] = f"Simulation mode set to {data['simulation_mode']}"
            
    except Exception as e:
        response = {'status': 'error', 'message': str(e)}
        
    return jsonify(response)

@app.route('/health')
def health():
    """Health check endpoint."""
    return "TeleMonitor Simulator is healthy"

def check_exporter_status(host, port):
    """Check if an exporter is available (simplified)."""
    # This is a mock function - in a real system it would check connectivity
    return {
        'status': 'active',
        'address': f"{host}:{port}"
    }

# Simulator functions
def generate_diameter_metrics():
    """Generate Diameter protocol metrics."""
    request_types = ['CCR', 'AAR', 'RAR', 'STR']
    error_types = ['TIMEOUT', 'AUTHENTICATION_FAILED', 'UNKNOWN_SESSION', 'NETWORK_ERROR']
    applications = ['Gx', 'Gy', 'Ro', 'Rf', 'S6a']
    
    for req_type in request_types:
        # Increment the request counter
        increment = random.randint(1, 20)
        diameter_requests.labels(type=req_type).inc(increment)
        
        # Update latency
        latency = random.uniform(20, 300)
        diameter_latency.labels(type=req_type).set(latency)
    
    # Simulate errors (less frequent)
    if random.random() < 0.3:  # 30% chance of generating an error
        error_type = random.choice(error_types)
        diameter_errors.labels(error_type=error_type).inc()
    
    # Update active sessions
    for app in applications:
        current = diameter_active_sessions.labels(application=app)._value.get() or 0
        change = random.randint(-50, 50)
        new_value = max(0, current + change)
        diameter_active_sessions.labels(application=app).set(new_value)
        
    # Update history
    if len(metrics_history['diameter_requests']) >= MAX_HISTORY_SIZE:
        metrics_history['diameter_requests'].pop(0)
    
    total_requests = sum([diameter_requests.labels(type=t)._value.get() or 0 for t in request_types])
    metrics_history['diameter_requests'].append(total_requests)

def generate_voip_metrics():
    """Generate VoIP metrics."""
    # Simulate the active VoIP calls with a trend
    current_calls = voip_calls._value.get() or 0
    trend = random.uniform(-30, 30)  # Trend up or down
    new_calls = max(0, min(500, current_calls + trend))  # Limit between 0 and 500
    voip_calls.set(new_calls)
    
    # Update history
    if len(metrics_history['timestamp']) >= MAX_HISTORY_SIZE:
        metrics_history['timestamp'].pop(0)
        metrics_history['voip_calls'].pop(0)
    
    metrics_history['timestamp'].append(time.time())
    metrics_history['voip_calls'].append(new_calls)
    
    # Simulate call quality by codec
    codecs = ['G.711', 'G.729', 'Opus', 'AMR-WB']
    for codec in codecs:
        # MOS Score (1-5)
        mos = random.uniform(3.0, 4.8)
        voip_quality.labels(codec=codec).set(mos)
        
        # Jitter
        jitter = random.uniform(5, 60)
        voip_jitter.labels(codec=codec).set(jitter)
        
        # Packet loss
        loss = random.uniform(0, 5)
        voip_packet_loss.labels(codec=codec).set(loss)
        
        # Call setup time
        setup_time = random.uniform(50, 2000)
        voip_call_setup_time.labels(codec=codec).observe(setup_time)

def generate_ipsec_metrics():
    """Generate IPsec metrics."""
    # Simulate the IPsec tunnels
    tunnel_states = ['established', 'connecting', 'failed']
    counts = [random.randint(10, 50), random.randint(0, 5), random.randint(0, 3)]
    
    for state, count in zip(tunnel_states, counts):
        ipsec_tunnels.labels(state=state).set(count)
    
    # Update history
    total_tunnels = sum(counts)
    if len(metrics_history['ipsec_tunnels']) >= MAX_HISTORY_SIZE:
        metrics_history['ipsec_tunnels'].pop(0)
    
    if len(metrics_history['ipsec_tunnels']) < len(metrics_history['timestamp']):
        metrics_history['ipsec_tunnels'].append(total_tunnels)
    
    # Simulate the bandwidth of tunnels
    for i in range(1, 6):  # 5 most active tunnels
        bandwidth = random.uniform(5, 100)  # Mbps
        ipsec_bandwidth.labels(tunnel_id=f"tunnel_{i}").set(bandwidth)
        
        # Latency
        latency = random.uniform(10, 150)  # ms
        ipsec_latency.labels(tunnel_id=f"tunnel_{i}").set(latency)
    
    # Occasionally simulate crypto errors
    if random.random() < 0.1:  # 10% chance
        error_types = ['integrity_check', 'decrypt_failure', 'invalid_key']
        error_type = random.choice(error_types)
        ipsec_crypto_errors.labels(error_type=error_type).inc()

def generate_mobile_metrics():
    """Generate mobile network metrics."""
    # Subscriber counts by type
    subscriber_types = ['prepaid', 'postpaid', 'iot', 'roaming']
    for sub_type in subscriber_types:
        current = mobile_subscribers.labels(type=sub_type)._value.get() or 0
        change = random.randint(-100, 100)
        new_value = max(0, current + change)
        mobile_subscribers.labels(type=sub_type).set(new_value)
    
    # Data traffic by generation
    generations = ['3G', '4G', '5G']
    for gen in generations:
        traffic = random.uniform(0.5, 20)  # Gbps
        mobile_data_traffic.labels(generation=gen).set(traffic)
        
        # Signal quality by cell
        for cell_id in range(1, 4):  # Sample cell IDs
            quality = random.uniform(40, 95)  # 0-100 scale
            mobile_signal_quality.labels(generation=gen, cell_id=f"cell_{cell_id}").set(quality)
    
    # Handover operations
    results = ['success', 'failure', 'rejected']
    for result in results:
        if random.random() < 0.5:  # 50% chance
            mobile_handovers.labels(result=result).inc(random.randint(1, 10))
    
    # Update history
    total_subscribers = sum([mobile_subscribers.labels(type=t)._value.get() or 0 for t in subscriber_types])
    if len(metrics_history['mobile_subscribers']) >= MAX_HISTORY_SIZE:
        metrics_history['mobile_subscribers'].pop(0)
    
    if len(metrics_history['mobile_subscribers']) < len(metrics_history['timestamp']):
        metrics_history['mobile_subscribers'].append(total_subscribers)

def generate_metrics():
    """Main function to generate all telecom metrics."""
    while True:
        try:
            generate_diameter_metrics()
            generate_voip_metrics()
            generate_ipsec_metrics()
            generate_mobile_metrics()
            logger.info("Generated telecom metrics")
            time.sleep(SIMULATION_INTERVAL)
        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            time.sleep(10)  # Longer sleep on error

# Main application startup
if __name__ == "__main__":
    # Start the Prometheus metrics server
    start_http_server(8000)
    logger.info("Metrics server started on port 8000")
    
    # Start the metrics generator in a background thread
    metrics_thread = threading.Thread(target=generate_metrics, daemon=True)
    metrics_thread.start()
    logger.info("Metrics generator started")
    
    # Start the Flask application
    logger.info("Starting web application on port 5000")
    app.run(host='0.0.0.0', port=5000)
