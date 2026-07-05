# Captures et preuves a fournir - SOCket

Ce fichier liste les captures conseillees pour le rapport ou la soutenance.

## 1. Plateforme lancee

Commande:

```bash
docker compose ps
```

Preuve attendue:

- `socket-nginx` actif;
- `socket-frontend` actif;
- `socket-backend` actif;
- `socket-postgres` healthy;
- `socket-elasticsearch` actif.

## 2. Page de connexion

Capture:

- navigateur sur `http://localhost`;
- formulaire utilisateur/mot de passe visible.

## 3. Dashboard SOC

Capture:

- nombre d incidents;
- incidents critiques;
- tableau des incidents;
- detail d un incident.

## 4. Workflow incident

Capture:

- incident selectionne;
- statut;
- assignation;
- preuves;
- recommandation;
- chronologie.

## 5. Simulation d attaque

Commande:

```bash
bash pentest/simulate_attack.sh
```

Capture:

- sortie terminal montrant les probes HTTP;
- retour JSON du capteur IDS;
- nouvel incident visible dans l interface.

## 6. PostgreSQL

Commande:

```bash
docker exec -it socket-postgres psql -U admin -d socket_db
```

Requetes:

```sql
\dt
SELECT id, username, role FROM users;
SELECT id, title, severity, status, attack_type, score FROM incidents ORDER BY created_at DESC LIMIT 5;
```

Capture:

- tables SQL visibles;
- incidents visibles.

## 7. Elasticsearch

Commandes:

```bash
curl -s http://localhost/api/v1/logs/recent
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! http://localhost:9200/_cat/indices?v
```

Capture:

- index `socket-events`;
- evenements recents.

## 8. Hardening Nginx

Commande:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/.env
```

Preuve attendue:

```text
404
```

## 9. PRA

Commande:

```bash
bash infra/scripts/backup_pra.sh
ls -lh infra/backups
sha256sum -c infra/backups/*.sha256
```

Capture:

- dump SQL;
- fichier `.sha256`;
- verification `OK`.

## 10. Git

Commande:

```bash
git status
```

Preuve attendue:

- code versionne;
- `.env` non versionne;
- documentation presente.
