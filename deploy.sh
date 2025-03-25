#!/bin/bash
set -e

# Color definitions
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Default options
PRESET="basic"
STORAGE_DIR="./data"
DATA_RETENTION="15d"
WEB_PORT=5000
GRAFANA_PORT=3000
PROMETHEUS_PORT=9090

# Show help function
show_help() {
    echo "TeleMonitor - Telecom Monitoring & Simulation"
    echo ""
    echo "Usage: ./deploy.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --preset <name>          Deployment preset (default: basic)"
    echo "                           Available: basic, complete, telco-core, diameter-only, voip-only"
    echo "  --storage <path>         Data storage directory (default: ./data)"
    echo "  --retention <period>     Data retention period (default: 15d)"
    echo "  --web-port <port>        Web interface port (default: 5000)"
    echo "  --grafana-port <port>    Grafana port (default: 3000)"
    echo "  --prometheus-port <port> Prometheus port (default: 9090)"
    echo "  --stop                   Stop running services"
    echo "  --status                 Check service status"
    echo "  --logs                   Show service logs"
    echo "  --help                   Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh                                # Deploy with basic preset"
    echo "  ./deploy.sh --preset complete              # Deploy all components"
    echo "  ./deploy.sh --preset voip-only --stop      # Stop VoIP monitoring"
    echo "  ./deploy.sh --storage /opt/telemonitor     # Use specific storage directory"
}

# Process arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --preset) PRESET="$2"; shift ;;
        --storage) STORAGE_DIR="$2"; shift ;;
        --retention) DATA_RETENTION="$2"; shift ;;
        --web-port) WEB_PORT="$2"; shift ;;
        --grafana-port) GRAFANA_PORT="$2"; shift ;;
        --prometheus-port) PROMETHEUS_PORT="$2"; shift ;;
        --stop) STOP=true ;;
        --status) STATUS=true ;;
        --logs) LOGS=true ;;
        --help) show_help; exit 0 ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; show_help; exit 1 ;;
    esac
    shift
done

echo -e "${BLUE}=== TeleMonitor - Telecom Monitoring & Simulation ===${NC}"

# Detect Docker installation and version
check_prerequisites() {
    echo -e "${BLUE}Checking prerequisites...${NC}"
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
        exit 1
    fi
    
    # Check Docker Compose
    if command -v docker-compose &> /dev/null; then
        DOCKER_COMPOSE="docker-compose"
    elif docker compose version &> /dev/null; then
        DOCKER_COMPOSE="docker compose"
    else
        echo -e "${RED}Docker Compose is not installed (neither as 'docker-compose' nor as 'docker compose').${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Prerequisites check passed${NC}"
    echo -e "Using command: ${YELLOW}$DOCKER_COMPOSE${NC}"
}

# Create necessary directories
prepare_environment() {
    echo -e "${BLUE}Preparing environment...${NC}"
    
    # Create storage directories
    mkdir -p "${STORAGE_DIR}/prometheus"
    mkdir -p "${STORAGE_DIR}/grafana"
    
    # Set environment variables for docker-compose
    export TELEMONITOR_STORAGE_DIR="${STORAGE_DIR}"
    export TELEMONITOR_DATA_RETENTION="${DATA_RETENTION}"
    export TELEMONITOR_WEB_PORT="${WEB_PORT}"
    export TELEMONITOR_GRAFANA_PORT="${GRAFANA_PORT}"
    export TELEMONITOR_PROMETHEUS_PORT="${PROMETHEUS_PORT}"
    
    echo -e "${GREEN}✓ Environment prepared${NC}"
}

# Validate preset
validate_preset() {
    echo -e "${BLUE}Validating preset: ${YELLOW}${PRESET}${NC}"
    
    if [[ ! -f "docker/presets/${PRESET}.yml" ]]; then
        echo -e "${RED}Invalid preset: ${PRESET}${NC}"
        echo -e "Available presets:"
        for preset_file in docker/presets/*.yml; do
            preset_name=$(basename "$preset_file" .yml)
            echo -e "  - ${YELLOW}${preset_name}${NC}"
        done
        exit 1
    fi
    
    echo -e "${GREEN}✓ Preset validated${NC}"
}

# Stop running services
stop_services() {
    echo -e "${BLUE}Stopping TeleMonitor services...${NC}"
    
    $DOCKER_COMPOSE -f docker/docker-compose.yml -f docker/presets/${PRESET}.yml down
    
    echo -e "${GREEN}✓ Services stopped${NC}"
}

# Check service status
check_status() {
    echo -e "${BLUE}Checking TeleMonitor services status...${NC}"
    
    $DOCKER_COMPOSE -f docker/docker-compose.yml -f docker/presets/${PRESET}.yml ps
}

# Show service logs
show_logs() {
    echo -e "${BLUE}Showing TeleMonitor services logs...${NC}"
    
    $DOCKER_COMPOSE -f docker/docker-compose.yml -f docker/presets/${PRESET}.yml logs --tail=100
}

# Start services
start_services() {
    echo -e "${BLUE}Starting TeleMonitor services with preset: ${YELLOW}${PRESET}${NC}"
    
    $DOCKER_COMPOSE -f docker/docker-compose.yml -f docker/presets/${PRESET}.yml up -d
    
    echo -e "${GREEN}✓ Services started${NC}"
}

# Display access information
show_access_info() {
    echo -e "${BLUE}Access Information:${NC}"
    echo -e "- TeleMonitor Simulator: ${GREEN}http://localhost:${WEB_PORT}${NC}"
    echo -e "- Grafana: ${GREEN}http://localhost:${GRAFANA_PORT}${NC} (login: admin/admin)"
    echo -e "- Prometheus: ${GREEN}http://localhost:${PROMETHEUS_PORT}${NC}"
    
    # Show additional access information based on preset
    case $PRESET in
        complete)
            echo -e "- Diameter Exporter: ${GREEN}http://localhost:9111${NC}"
            echo -e "- VoIP Exporter: ${GREEN}http://localhost:9010${NC}"
            echo -e "- IPsec Exporter: ${GREEN}http://localhost:8079${NC}"
            ;;
        diameter-only)
            echo -e "- Diameter Exporter: ${GREEN}http://localhost:9111${NC}"
            ;;
        voip-only)
            echo -e "- VoIP Exporter: ${GREEN}http://localhost:9010${NC}"
            ;;
    esac
}

# Main execution
check_prerequisites

if [[ -n "$STOP" ]]; then
    validate_preset
    stop_services
    exit 0
fi

if [[ -n "$STATUS" ]]; then
    validate_preset
    check_status
    exit 0
fi

if [[ -n "$LOGS" ]]; then
    validate_preset
    show_logs
    exit 0
fi

validate_preset
prepare_environment
start_services
show_access_info
