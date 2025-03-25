# TeleMonitor

Un projet de simulation et de monitoring d'infrastructures de télécommunications.

## Fonctionnalités

- **Simulateur de télécommunications**: Génère des métriques réalistes pour les protocoles télécom
- **Exporteurs spécialisés**: Diameter, VoIP, IPsec
- **Monitoring complet**: Prometheus, Grafana avec dashboards préconfigurés
- **Déploiement flexible**: Docker ou Ansible, à votre choix

## Déploiement rapide

Pour un déploiement complet avec Docker:

```bash
./deploy.sh
```

> **Note**: Le script est compatible avec les deux versions de Docker Compose : l'ancienne commande `docker-compose` et la nouvelle syntaxe `docker compose` intégrée comme plugin Docker.

## Options de déploiement

Déployer seulement certains composants:

```bash
./deploy.sh --components simulator,monitoring
```

Utiliser Ansible au lieu de Docker:

```bash
./deploy.sh --mode ansible
```

Voir toutes les options:

```bash
./deploy.sh --help
```

## Composants disponibles

- **simulator**: Interface web et générateur de métriques
- **monitoring**: Prometheus et Grafana
- **diameter**: Exporteur pour le protocole Diameter
- **voip**: Monitoring VoIP

## Accès aux services

- Simulateur: http://localhost:5000
- Grafana: http://localhost:3000 (admin/admin)
- Prometheus: http://localhost:9090