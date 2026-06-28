# Utilisation d'une image Python légère et sécurisée
FROM python:3.11-slim

# Définition du répertoire de travail dans le conteneur
WORKDIR /app

# Copie des dépendances et installation
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste du code de l'API
COPY . .

# Exposition du port de l'API
EXPOSE 8000

# Commande pour lancer le serveur
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]