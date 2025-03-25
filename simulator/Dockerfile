FROM python:3.9-slim

WORKDIR /app

# Installer les dépendances
RUN pip install --no-cache-dir flask prometheus_client

# Copier les fichiers de l'application
COPY . /app/

# Exposer les ports
EXPOSE 5000 8000

# Démarrer l'application
CMD ["python", "app.py"]