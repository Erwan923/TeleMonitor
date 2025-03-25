#!/usr/bin/env python3
from flask import Flask, render_template, jsonify
from prometheus_client import start_http_server, Gauge, Counter
import threading
import time
import random
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TeleMonitor')

# Initialisation Flask
app = Flask(__name__)

# Métriques Prometheus pour télécommunications
# Métriques Diameter
diameter_requests = Counter('telecom_diameter_requests_total', 'Total des requêtes Diameter', ['type'])
diameter_latency = Gauge('telecom_diameter_latency_ms', 'Latence Diameter en ms', ['type'])
diameter_errors = Counter('telecom_diameter_errors_total', 'Erreurs Diameter', ['error_type'])

# Métriques VoIP
voip_calls = Gauge('telecom_voip_active_calls', 'Appels VoIP actifs')
voip_quality = Gauge('telecom_voip_mos', 'Score qualité MOS (1-5)', ['codec'])
voip_jitter = Gauge('telecom_voip_jitter_ms', 'Gigue VoIP en ms', ['codec'])
voip_packet_loss = Gauge('telecom_voip_packet_loss_percent', 'Pourcentage de perte de paquets VoIP', ['codec'])

# Métriques IPsec
ipsec_tunnels = Gauge('telecom_ipsec_tunnels', 'Tunnels IPsec actifs', ['state'])
ipsec_bandwidth = Gauge('telecom_ipsec_bandwidth_mbps', 'Bande passante IPsec (Mbps)', ['tunnel_id'])

# Données pour API REST
metrics_history = {
    'timestamp': [],
    'diameter_requests': [],
    'voip_calls': [],
    'ipsec_tunnels': []
}

# Routes Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/metrics')
def get_metrics():
    return jsonify(metrics_history)

# Générateur de métriques télécom
def generate_diameter_metrics():
    request_types = ['CCR', 'AAR', 'RAR', 'STR']
    error_types = ['TIMEOUT', 'AUTHENTICATION_FAILED', 'UNKNOWN_SESSION']
    
    for req_type in request_types:
        # Incrémenter le compteur de requêtes
        increment = random.randint(1, 20)
        diameter_requests.labels(type=req_type).inc(increment)
        
        # Mise à jour de la latence
        latency = random.uniform(20, 300)
        diameter_latency.labels(type=req_type).set(latency)
    
    # Simuler des erreurs (moins fréquentes)
    if random.random() < 0.3:  # 30% de chance de générer une erreur
        error_type = random.choice(error_types)
        diameter_errors.labels(error_type=error_type).inc()

def generate_voip_metrics():
    # Simuler les appels VoIP actifs avec une tendance
    current_calls = voip_calls._value.get() or 0
    trend = random.uniform(-30, 30)  # Tendance à la hausse ou à la baisse
    new_calls = max(0, min(500, current_calls + trend))  # Limites de 0 à 500
    voip_calls.set(new_calls)
    
    # Mettre à jour l'historique
    if len(metrics_history['timestamp']) >= 50:
        metrics_history['timestamp'].pop(0)
        metrics_history['voip_calls'].pop(0)
    
    metrics_history['timestamp'].append(time.time())
    metrics_history['voip_calls'].append(new_calls)
    
    # Simuler la qualité des appels par codec
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

def generate_ipsec_metrics():
    # Simuler les tunnels IPsec
    tunnel_states = ['established', 'connecting', 'failed']
    counts = [random.randint(10, 50), random.randint(0, 5), random.randint(0, 3)]
    
    for state, count in zip(tunnel_states, counts):
        ipsec_tunnels.labels(state=state).set(count)
    
    # Mettre à jour l'historique
    total_tunnels = sum(counts)
    if len(metrics_history['timestamp']) >= 50:
        metrics_history['ipsec_tunnels'].pop(0)
    if len(metrics_history['ipsec_tunnels']) < len(metrics_history['timestamp']):
        metrics_history['ipsec_tunnels'].append(total_tunnels)
    
    # Simuler la bande passante des tunnels
    for i in range(1, 6):  # 5 tunnels les plus actifs
        bandwidth = random.uniform(5, 100)  # Mbps
        ipsec_bandwidth.labels(tunnel_id=f"tunnel_{i}").set(bandwidth)

def generate_metrics():
    while True:
        try:
            generate_diameter_metrics()
            generate_voip_metrics()
            generate_ipsec_metrics()
            logger.info("Métriques générées")
            time.sleep(5)
        except Exception as e:
            logger.error(f"Erreur lors de la génération de métriques: {e}")
            time.sleep(10)  # Attendre plus longtemps en cas d'erreur

# Démarrage
if __name__ == "__main__":
    # Démarrer le serveur de métriques Prometheus
    start_http_server(8000)
    logger.info("Serveur de métriques démarré sur le port 8000")
    
    # Démarrer le générateur de métriques dans un thread séparé
    metrics_thread = threading.Thread(target=generate_metrics, daemon=True)
    metrics_thread.start()
    logger.info("Générateur de métriques démarré")
    
    # Démarrer l'application Flask
    logger.info("Démarrage de l'application web sur le port 5000")
    app.run(host='0.0.0.0', port=5000)