#!/bin/bash
set -euo pipefail

DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_DIR="./infra/backups"
CONTAINER_NAME="socket-postgres"
DB_USER="${POSTGRES_USER:-admin}"
DB_NAME="${POSTGRES_DB:-socket_db}"
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

mkdir -p "$BACKUP_DIR"
echo "Initialisation sauvegarde PRA PostgreSQL..."
docker exec -t "$CONTAINER_NAME" pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"
sha256sum "$BACKUP_FILE" > "$BACKUP_FILE.sha256"
echo "Sauvegarde creee: $BACKUP_FILE"
echo "Empreinte SHA256: $BACKUP_FILE.sha256"
