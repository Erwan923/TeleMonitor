# TeleMonitor

A comprehensive telecommunications simulation and monitoring platform that generates realistic metrics for telecom protocols and provides specialized visualization.

## Key Features

- **Telecom Protocol Simulation**: Realistic simulation of Diameter, VoIP, and IPsec protocols
- **Specialized Exporters**: Purpose-built exporters for telecom-specific protocols
- **Pre-configured Dashboards**: Ready-to-use Grafana dashboards for telecom metrics
- **Flexible Deployment**: Simple deployment with various preset configurations
- **Interactive Controls**: Adjust simulation parameters through an intuitive web interface

## Quick Start

The simplest way to get started is using the included deployment script:

```bash
./deploy.sh
```

This will deploy the basic preset with core components. To deploy all components:

```bash
./deploy.sh --preset complete
```

## Deployment Options

TeleMonitor offers several deployment presets:

- `basic`: Core components only (simulator, Prometheus, Grafana)
- `complete`: All components including specialized exporters and alerting
- `telco-core`: Focus on telecom protocol exporters
- `diameter-only`: Only Diameter protocol monitoring
- `voip-only`: Only VoIP monitoring

Additional deployment options:

```bash
# Specify a custom data storage location
./deploy.sh --storage /opt/telemonitor

# Set a custom data retention period
./deploy.sh --retention 30d

# Use custom ports
./deploy.sh --web-port 8080 --grafana-port 8000 --prometheus-port 8090

# Stop services
./deploy.sh --stop

# Check service status
./deploy.sh --status

# View service logs
./deploy.sh --logs
```

## Components

### Core Components

- **Simulator**: Web interface and metric generator
- **Prometheus**: Time-series database for metrics
- **Grafana**: Visualization platform with pre-configured dashboards

### Specialized Exporters

- **Diameter Exporter**: Monitors Diameter protocol used in mobile networks
- **VoIP Exporter**: Tracks Voice over IP metrics including quality scores
- **IPsec Exporter**: Monitors IPsec tunnel status and performance

## Access Services

After deployment, services are available at:

- **Simulator Web UI**: http://localhost:5000
- **Grafana**: http://localhost:3000 (login: admin/admin)
- **Prometheus**: http://localhost:9090

## Available Metrics

TeleMonitor simulates and exposes various telecom-specific metrics:

### Diameter Protocol
- Request/response rates by type (CCR, AAR, RAR, STR)
- Latency measurements
- Error rates by type
- Active sessions

### VoIP
- Active call count
- Call quality (MOS score)
- Jitter, packet loss, and latency
- Codec-specific metrics

### IPsec
- Tunnel status (established, connecting, failed)
- Bandwidth usage
- Latency and packet loss
- Cryptographic errors

### Mobile Network
- Subscriber metrics
- Data traffic by generation (3G, 4G, 5G)
- Signal quality
- Handover operations

## Customization

TeleMonitor is designed to be easily customizable. The most common customizations are:

- Adding new protocol exporters
- Creating custom Grafana dashboards
- Modifying simulation parameters
- Adding new alert rules

## Requirements

- Docker and Docker Compose
- 2GB RAM minimum (4GB recommended for complete installation)
- 1GB free disk space minimum

## License

TeleMonitor is open source software licensed under the MIT license.
