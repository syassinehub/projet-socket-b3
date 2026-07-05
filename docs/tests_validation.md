# Tests et validation - SOCket

Ce document liste les tests a executer avant la soutenance.

## 1. Etat des conteneurs

```bash
docker compose ps
```

Resultat attendu:

- `socket-nginx`: `Up`;
- `socket-frontend`: `Up`;
- `socket-backend`: `Up`;
- `socket-postgres`: `Up` et `healthy`;
- `socket-elasticsearch`: `Up`.

## 2. Test frontend

```bash
curl -s -i http://localhost/ | sed -n '1,20p'
```

Resultat attendu:

```text
HTTP/1.1 200 OK
```

## 3. Test API protegee

```bash
curl -s -i http://localhost/api/v1/incidents | sed -n '1,40p'
```

Resultat attendu:

```text
HTTP/1.1 401 Unauthorized
{"detail":"Authentification requise"}
```

Ce resultat est positif: l API fonctionne et refuse les appels non authentifies.

## 4. Test authentification

```bash
python3 - <<'PY'
import json
import urllib.request

payload = json.dumps({"username": "admin", "password": "Admin123!"}).encode()
req = urllib.request.Request(
    "http://localhost/api/v1/auth/login",
    data=payload,
    headers={"Content-Type": "application/json"},
    method="POST",
)
print(urllib.request.urlopen(req, timeout=5).read().decode())
PY
```

Resultat attendu:

- presence de `access_token`;
- utilisateur `admin`;
- role `admin`.

## 5. Test protection chemins sensibles

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/.env
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/.git/config
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/phpmyadmin
```

Resultat attendu:

```text
404
404
404
```

## 6. Test IDS complet

```bash
bash pentest/simulate_attack.sh
bash pentest/attack_web_vectors.sh
```

Resultat attendu:

- des requetes HTTP sont envoyees;
- le script ingere les alertes Suricata EVE JSON;
- l API renvoie un JSON avec les detections;
- de nouveaux incidents apparaissent dans le tableau de bord.

## 7. Test SQL

```bash
docker exec -it socket-postgres psql -U admin -d socket_db
```

Puis:

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM incidents;
SELECT COUNT(*) FROM incident_events;
\q
```

Resultat attendu:

- au moins 2 utilisateurs;
- au moins 1 incident;
- des evenements de chronologie.

## 8. Test Elasticsearch

Depuis l interface, se connecter en `admin`, ouvrir `Donnees`, puis l onglet `Elasticsearch`.

Verification directe en terminal:

```bash
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! http://localhost:9200/_cat/indices?v
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! "http://localhost:9200/socket-events/_search?pretty&size=5"
```

Resultat attendu:

- index `socket-events` present;
- evenements de type `auth.success`, `incident.created` ou `incident.updated` selon les actions effectuees.

## 9. Test PRA

```bash
bash infra/scripts/backup_pra.sh
ls -lh infra/backups
```

Resultat attendu:

- un fichier `db_backup_YYYY-MM-DD_HH-MM-SS.sql`;
- un fichier `.sha256` associe.

Verifier l empreinte:

```bash
sha256sum -c infra/backups/*.sha256
```

## 10. Test syntaxe scripts et backend

```bash
python3 -m py_compile backend/main.py backend/suricata.py infra/scripts/ingest_suricata_eve.py
bash -n pentest/simulate_attack.sh
bash -n pentest/attack_web_vectors.sh
bash -n pentest/attack_sqli.sh
bash -n pentest/attack_bruteforce.sh
bash -n infra/scripts/backup_pra.sh
```

Resultat attendu:

- aucune erreur.

## 11. Checklist avant rendu

- Le projet demarre avec `docker compose up -d --build`.
- Le login fonctionne.
- Les incidents sont visibles.
- Les simulations generent de nouvelles alertes.
- PostgreSQL contient les donnees metier.
- Elasticsearch contient les evenements.
- Le PRA cree une sauvegarde.
- La documentation est presente dans `docs/`.
- Le code est pousse sur Git sans `.env`.

## 12. Captures conseillees

- `docker compose ps` avec les services actifs.
- Page de connexion et dashboard SOCket.
- Detail d un incident avec preuves, score et recommandation.
- Vue `Donnees` avec PostgreSQL et Elasticsearch.
- Sortie d un script de pentest.
- Sauvegarde PRA avec fichier SQL et empreinte SHA256.
- Trello ou outil de suivi de projet.
