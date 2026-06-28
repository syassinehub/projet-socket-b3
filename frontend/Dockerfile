# Utilisation d'une image Node.js légère
FROM node:18-alpine

# Définition du répertoire de travail
WORKDIR /app

# Copie des fichiers de configuration NPM
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du code source
COPY . .

# Exposition du port de Vite (Vue.js)
EXPOSE 5173

# Commande pour lancer le serveur de développement en l'exposant au réseau Docker
CMD ["npm", "run", "dev", "--", "--host"]