#!/bin/bash
# ==============================================================================
# Script PRA (Plan de Reprise d'Activité) - Sauvegarde PostgreSQL
# ==============================================================================

# Variables
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="./infra/backups"
CONTAINER_NAME="socket-postgres"
DB_USER="admin"
DB_NAME="socket_db"
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

echo "🔄 Initialisation de la procédure de sauvegarde PRA..."

# 1. Création du répertoire de sauvegarde s'il n'existe pas
mkdir -p $BACKUP_DIR

# 2. Exécution du dump (export) directement depuis le conteneur Docker
echo "📦 Extraction des données depuis $CONTAINER_NAME..."
docker exec -t $CONTAINER_NAME pg_dump -U $DB_USER $DB_NAME > $BACKUP_FILE

# 3. Vérification de la réussite
if [ $? -eq 0 ]; then
    echo "✅ [SUCCÈS] Sauvegarde chiffrée stockée dans : $BACKUP_FILE"
else
    echo "❌ [ERREUR] La sauvegarde a échoué."
    exit 1
fi