#!/bin/bash
set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Variables par défaut
MODE="docker"
COMPONENTS=("all")

# Fonction d'aide
show_help() {
    echo "Usage: ./deploy.sh [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --mode <docker|ansible>    Mode de déploiement (défaut: docker)"
    echo "  --components <comp1,comp2> Composants à déployer, séparés par virgules"
    echo "                            Valeurs possibles: all, simulator, monitoring, diameter, voip"
    echo "  --help                    Affiche cette aide"
    echo ""
    echo "Exemples:"
    echo "  ./deploy.sh                                 # Déploie tout avec Docker"
    echo "  ./deploy.sh --mode ansible                  # Déploie tout avec Ansible"
    echo "  ./deploy.sh --components simulator,monitoring # Déploie seulement le simulateur et le monitoring"
}

# Traiter les arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --mode) MODE="$2"; shift ;;
        --components) IFS=',' read -r -a COMPONENTS <<< "$2"; shift ;;
        --help) show_help; exit 0 ;;
        *) echo "Option inconnue: $1"; show_help; exit 1 ;;
    esac
    shift
done

echo -e "${BLUE}=== TeleMonitor - Déploiement ===${NC}"
echo -e "Mode: ${YELLOW}$MODE${NC}"
echo -e "Composants: ${YELLOW}${COMPONENTS[*]}${NC}"

# Vérifier les prérequis
if [ "$MODE" == "docker" ]; then
    which docker > /dev/null || { echo "Docker n'est pas installé"; exit 1; }
    
    # Vérifier si docker-compose est disponible (ancienne version)
    if which docker-compose > /dev/null 2>&1; then
        DOCKER_COMPOSE="docker-compose"
    # Vérifier si docker compose est disponible (nouvelle version)
    elif docker compose version > /dev/null 2>&1; then
        DOCKER_COMPOSE="docker compose"
    else
        echo "Docker Compose n'est pas installé (ni comme 'docker-compose' ni comme 'docker compose')"
        exit 1
    fi
    
    echo -e "Utilisation de la commande: ${YELLOW}$DOCKER_COMPOSE${NC}"
elif [ "$MODE" == "ansible" ]; then
    which ansible > /dev/null || { echo "Ansible n'est pas installé"; exit 1; }
fi

# Déploiement Docker
if [ "$MODE" == "docker" ]; then
    echo -e "${BLUE}Déploiement avec Docker...${NC}"
    
    # Construire la commande docker-compose
    # Toujours inclure le fichier principal pour les définitions de réseau et volumes
    COMPOSE_FILES="-f docker-compose.yml"
    
    # Si ce n'est pas "all", ajouter seulement les fichiers pertinents
    if [[ ! " ${COMPONENTS[*]} " =~ " all " ]]; then
        for component in "${COMPONENTS[@]}"; do
            if [ -f "docker/docker-compose/$component.yml" ]; then
                COMPOSE_FILES="$COMPOSE_FILES -f docker-compose/$component.yml"
            else
                echo -e "${YELLOW}Composant non trouvé: $component${NC}"
            fi
        done
    fi
    
    # Lancer docker-compose
    if [ -n "$COMPOSE_FILES" ]; then
        cd docker && $DOCKER_COMPOSE $COMPOSE_FILES up -d
    else
        echo "Aucun composant valide spécifié!"
        exit 1
    fi

# Déploiement Ansible    
elif [ "$MODE" == "ansible" ]; then
    echo -e "${BLUE}Déploiement avec Ansible...${NC}"
    
    # Si c'est "all", exécuter le playbook principal
    if [[ " ${COMPONENTS[*]} " =~ " all " ]]; then
        ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_all.yml
    else
        # Sinon, exécuter les playbooks individuels
        for component in "${COMPONENTS[@]}"; do
            if [ -f "ansible/playbooks/deploy_$component.yml" ]; then
                echo -e "Déploiement de: ${YELLOW}$component${NC}"
                ansible-playbook -i ansible/inventory.ini ansible/playbooks/deploy_$component.yml
            else
                echo -e "${YELLOW}Playbook non trouvé pour: $component${NC}"
            fi
        done
    fi
else
    echo "Mode non reconnu: $MODE"
    exit 1
fi

echo -e "${GREEN}Déploiement terminé!${NC}"

# Afficher les URLs des services
if [[ " ${COMPONENTS[*]} " =~ " simulator " || " ${COMPONENTS[*]} " =~ " all " ]]; then
    echo -e "- Simulateur: ${GREEN}http://localhost:5000${NC}"
fi
if [[ " ${COMPONENTS[*]} " =~ " monitoring " || " ${COMPONENTS[*]} " =~ " all " ]]; then
    echo -e "- Grafana: ${GREEN}http://localhost:3000${NC} (admin/admin)"
    echo -e "- Prometheus: ${GREEN}http://localhost:9090${NC}"
fi