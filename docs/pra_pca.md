# PCA/PRA - SOCket

## Objectif

Le PCA/PRA de SOCket vise a garantir que les incidents et leur chronologie peuvent etre sauvegardes puis restaures en cas de perte de donnees ou de panne.

## Perimetre couvert

- Base PostgreSQL: utilisateurs, incidents, chronologie.
- Fichiers de configuration versionnes: Docker, Nginx, scripts.
- Documentation de reprise.

Elasticsearch est utilise pour les logs et evenements techniques. Dans ce prototype, la priorite de restauration est PostgreSQL, car il contient les donnees metier critiques.

## Sauvegarde

Script:

```bash
bash infra/scripts/backup_pra.sh
```

Le script:

1. cree le dossier `infra/backups` si necessaire;
2. execute `pg_dump` dans le conteneur PostgreSQL;
3. genere un fichier SQL horodate;
4. genere une empreinte SHA256.

Exemple de resultat:

```text
infra/backups/db_backup_2026-07-02_10-30-00.sql
infra/backups/db_backup_2026-07-02_10-30-00.sql.sha256
```

Verifier l integrite:

```bash
sha256sum -c infra/backups/*.sha256
```

## Restauration

Exemple de restauration depuis un dump:

```bash
docker exec -i socket-postgres psql -U admin -d socket_db < infra/backups/db_backup_YYYY-MM-DD_HH-MM-SS.sql
```

Apres restauration:

```bash
docker compose restart api
```

Verifier:

```bash
docker exec -it socket-postgres psql -U admin -d socket_db
```

Puis:

```sql
SELECT COUNT(*) FROM incidents;
SELECT COUNT(*) FROM incident_events;
\q
```

## Procedure de reprise apres incident

1. Identifier la panne: API, SQL, proxy, frontend ou Elasticsearch.
2. Verifier les conteneurs:

```bash
docker compose ps
docker compose logs --tail=100 api
docker compose logs --tail=100 db-sql
```

3. Redemarrer les services si necessaire:

```bash
docker compose restart
```

4. Si la base SQL est perdue, restaurer le dernier dump valide.
5. Tester le login et l affichage des incidents.
6. Documenter l incident dans SOCket.

## PCA simplifie

Mesures de continuite:

- services isoles en conteneurs;
- redemarrage automatique `restart: unless-stopped`;
- volumes persistants Docker;
- sauvegarde SQL;
- documentation de relance;
- scripts de verification.

## Limites et ameliorations

- Automatiser une sauvegarde planifiee via cron.
- Ajouter une sauvegarde Elasticsearch.
- Stocker les sauvegardes hors machine locale.
- Tester regulierement la restauration sur un environnement vierge.
- Ajouter HTTPS et certificats pour une mise en production.
