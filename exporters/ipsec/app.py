# exporters/ipsec/app.py
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
logger = logging.getLogger('ipsec-exporter')

# Configuration from environment variables
LISTEN_PORT = int(os.environ.get('IPSEC_LISTEN_PORT', 8079))
SIMULATION_ENABLED = os.environ.get('IPSEC_SIMULATION_ENABLED', 'true').lower() == 'true'
SIMULATION_INTERVAL = int(os.environ.get('IPSEC_SIMULATION_INTERVAL', 5))

# Initialize Flask app
app = Flask(__name__)

# Initialize Prometheus metrics

# Tunnel state metrics
ipsec_tunnels = Gauge('telecom_ipsec_tunnels', 'IPsec tunnels by state', ['state'])
ipsec_tunnel_state = Gauge('telecom_ipsec_tunnel_state', 'IPsec tunnel state (1=up, 0=down)', ['tunnel_id', 'local_subnet', 'remote_subnet'])

# Tunnel performance metrics
ipsec_bandwidth = Gauge('telecom_ipsec_bandwidth_mbps', 'IPsec tunnel bandwidth (Mbps)', ['tunnel_id', 'direction'])
ipsec_packets = Counter('telecom_ipsec_packets_total', 'IPsec packets processed', ['tunnel_id', 'direction'])
ipsec_bytes = Counter('telecom_ipsec_bytes_total', 'IPsec bytes processed', ['tunnel_id', 'direction'])
ipsec_rekey_count = Counter('telecom_ipsec_rekey_total', 'IPsec rekey operations', ['tunnel_id'])

# Tunnel latency metrics
ipsec_latency = Gauge('telecom_ipsec_latency_ms', 'IPsec tunnel latency in milliseconds', ['tunnel_id'])
ipsec_packet_loss = Gauge('telecom_ipsec_packet_loss_percent', 'IPsec tunnel packet loss percentage', ['tunnel_id'])

# Security metrics
ipsec_crypto_errors = Counter('telecom_ipsec_crypto_errors_total', 'IPsec cryptographic errors', ['error_type'])
ipsec_auth_failures = Counter('telecom_ipsec_auth_failures_total', 'IPsec authentication failures', ['tunnel_id'])

@app.route('/metrics')
def metrics():
    """Endpoint to expose Prometheus metrics."""
    return Response(prometheus_client.generate_latest(), mimetype='text/plain')

@app.route('/health')
def health():
    """Health check endpoint."""
    return "IPsec Exporter is healthy"

def generate_ipsec_metrics():
    """Generate simulated IPsec tunnel metrics."""
    if not SIMULATION_ENABLED:
        logger.info("Simulation disabled, no metrics will be generated")
        return
    
    # Define tunnel states and sample tunnel IDs
    tunnel_states = ['established', 'connecting', 'rekeying', 'failed']
    tunnel_ids = [f'tunnel_{i}' for i in range(1, 11)]  # 10 example tunnels
    error_types = ['integrity_check', 'decrypt_failure', 'invalid_key', 'replay_error', 'bad_proposal']
    directions = ['in', 'out']
    
    # Define sample subnets for tunnels
    local_subnets = ['10.1.0.0/24', '10.2.0.0/24', '10.3.0.0/24', '172.16.0.0/16', '192.168.1.0/24']
    remote_subnets = ['192.168.10.0/24', '192.168.20.0/24', '172.31.0.0/16', '10.50.0.0/16', '10.60.0.0/16']
    
    # Initialize tunnel states
    ipsec_tunnels.labels(state='established').set(random.randint(5, 20))
    ipsec_tunnels.labels(state='connecting').set(random.randint(0, 3))
    ipsec_tunnels.labels(state='rekeying').set(random.randint(0, 2))
    ipsec_tunnels.labels(state='failed').set(random.randint(0, 5))
    
    # Initialize tunnel details
    for i, tunnel_id in enumerate(tunnel_ids):
        local_subnet = local_subnets[i % len(local_subnets)]
        remote_subnet = remote_subnets[i % len(remote_subnets)]
        
        # 80% chance the tunnel is up
        state = 1 if random.random() < 0.8 else 0
        ipsec_tunnel_state.labels(tunnel_id=tunnel_id, local_subnet=local_subnet, remote_subnet=remote_subnet).set(state)
        
        # Initialize performance metrics
        for direction in directions:
            ipsec_bandwidth.labels(tunnel_id=tunnel_id, direction=direction).set(random.uniform(5, 100))
            ipsec_packets.labels(tunnel_id=tunnel_id, direction=direction).inc(random.randint(1000, 10000))
            ipsec_bytes.labels(tunnel_id=tunnel_id, direction=direction).inc(random.randint(1000000, 10000000))
        
        # Initialize latency metrics
        ipsec_latency.labels(tunnel_id=tunnel_id).set(random.uniform(5, 100))
        ipsec_packet_loss.labels(tunnel_id=tunnel_id).set(random.uniform(0, 2))
    
    logger.info("Starting IPsec metrics simulation")
    
    while True:
        try:
            # Update tunnel states
            for state in tunnel_states:
                current = ipsec_tunnels.labels(state=state)._value.get() or 0
                change = random.randint(-2, 2)
                new_value = max(0, current + change)
                ipsec_tunnels.labels(state=state).set(new_value)
            
            # Update tunnel details
            for tunnel_id in tunnel_ids:
                # Occasionally flip tunnel state
                if random.random() < 0.05:  # 5% chance of state change
                    for label_dict, value in ipsec_tunnel_state._metrics.items():
                        if label_dict[0][1] == tunnel_id:  # Find the right tunnel
                            current_state = value._value.get() or 1
                            new_state = 1 - current_state  # Toggle between 0 and 1
                            ipsec_tunnel_state.labels(
                                tunnel_id=label_dict[0][1], 
                                local_subnet=label_dict[1][1], 
                                remote_subnet=label_dict[2][1]
                            ).set(new_state)
                
                # Update bandwidth (more variable)
                for direction in directions:
                    current_bw = ipsec_bandwidth.labels(tunnel_id=tunnel_id, direction=direction)._value.get() or 50
                    change = random.uniform(-20, 20)
                    new_bw = max(1, min(1000, current_bw + change))  # Between 1 and 1000 Mbps
                    ipsec_bandwidth.labels(tunnel_id=tunnel_id, direction=direction).set(new_bw)
                    
                    # Increment packet and byte counters
                    packet_count = random.randint(100, 1000)
                    byte_count = packet_count * random.randint(500, 1500)  # Random packet sizes
                    ipsec_packets.labels(tunnel_id=tunnel_id, direction=direction).inc(packet_count)
                    ipsec_bytes.labels(tunnel_id=tunnel_id, direction=direction).inc(byte_count)
                
                # Update latency and packet loss
                current_latency = ipsec_latency.labels(tunnel_id=tunnel_id)._value.get() or 20
                latency_change = random.uniform(-5, 5)
                new_latency = max(1, current_latency + latency_change)
                ipsec_latency.labels(tunnel_id=tunnel_id).set(new_latency)
                
                current_loss = ipsec_packet_loss.labels(tunnel_id=tunnel_id)._value.get() or 0.5
                loss_change = random.uniform(-0.2, 0.2)
                new_loss = max(0, min(10, current_loss + loss_change))
                ipsec_packet_loss.labels(tunnel_id=tunnel_id).set(new_loss)
                
                # Occasionally trigger a rekey
                if random.random() < 0.1:  # 10% chance
                    ipsec_rekey_count.labels(tunnel_id=tunnel_id).inc()
                
                # Rarely simulate authentication failures
                if random.random() < 0.03:  # 3% chance
                    ipsec_auth_failures.labels(tunnel_id=tunnel_id).inc()
            
            # Rarely simulate crypto errors
            if random.random() < 0.05:  # 5% chance
                error_type = random.choice(error_types)
                ipsec_crypto_errors.labels(error_type=error_type).inc(random.randint(1, 3))
            
            logger.debug("Generated IPsec metrics")
            time.sleep(SIMULATION_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error generating IPsec metrics: {e}")
            time.sleep(10)  # Longer sleep on error

if __name__ == '__main__':
    # Start metrics generation in a separate thread
    if SIMULATION_ENABLED:
        simulation_thread = threading.Thread(target=generate_ipsec_metrics, daemon=True)
        simulation_thread.start()
        logger.info(f"IPsec metrics simulation started with interval of {SIMULATION_INTERVAL}s")
    
    # Start the Flask server
    logger.info(f"Starting IPsec exporter on port {LISTEN_PORT}")
    app.run(host='0.0.0.0', port=LISTEN_PORT)
