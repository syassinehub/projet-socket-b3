# Bases de donnees et logs - SOCket

## Objectif

SOCket utilise deux types de stockage:

- PostgreSQL pour les donnees structurees du SOC.
- Elasticsearch pour les logs et evenements techniques.

Cela permet de couvrir le besoin SQL/NoSQL attendu dans le projet.

## PostgreSQL: donnees metier

### Interface graphique

Depuis le dashboard SOCket:

1. ouvrir `http://localhost`;
2. se connecter avec `admin / Admin123!`;
3. cliquer sur `Donnees`;
4. rester sur l onglet `PostgreSQL`.

Cette vue est reservee au role `admin`. L interface affiche `users`, `incidents` et `incident_events`. Les hashes de mots de passe ne sont pas affiches.

### Terminal

Connexion:

```bash
docker exec -it socket-postgres psql -U admin -d socket_db
```

Lister les tables:

```sql
\dt
```

Tables principales:

| Table | Role |
| --- | --- |
| `users` | Comptes utilisateurs et roles |
| `incidents` | Incidents de securite, score, severite, statut |
| `incident_events` | Chronologie, commentaires et actions analystes |

Requetes utiles:

```sql
SELECT id, username, role, created_at FROM users;

SELECT id, title, source_ip, attack_type, severity, score, status, created_at
FROM incidents
ORDER BY created_at DESC
LIMIT 10;

SELECT incident_id, actor, event_type, message, created_at
FROM incident_events
ORDER BY created_at DESC
LIMIT 10;
```

Quitter:

```sql
\q
```

## Elasticsearch: logs et evenements

### Interface graphique

Depuis le dashboard SOCket:

1. ouvrir `http://localhost`;
2. se connecter avec `admin / Admin123!`;
3. cliquer sur `Donnees`;
4. ouvrir l onglet `Elasticsearch`.

Cette vue est reservee au role `admin`. L interface affiche les derniers documents de l index `socket-events`.

### Terminal

Via l API SOCket:

```bash
curl -s http://localhost/api/v1/logs/recent
```

Voir les index:

```bash
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! http://localhost:9200/_cat/indices?v
```

Voir les derniers documents:

```bash
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! "http://localhost:9200/socket-events/_search?pretty&size=5"
```

Evenements typiques:

- `auth.success`: connexion reussie;
- `auth.failed`: echec de connexion;
- `incident.created`: creation d incident;
- `incident.updated`: changement de statut, severite ou assignation;
- `incident.comment`: commentaire d investigation.

## Alertes Suricata

Suricata ecrit ses alertes au format EVE JSON dans:

```text
infra/suricata/logs/eve.json
```

Le script d ingestion lit ce fichier et cree les incidents dans SOCket:

```bash
python3 infra/scripts/ingest_suricata_eve.py
```

Pour une demonstration reproductible:

```bash
python3 infra/scripts/ingest_suricata_eve.py --sample
```

## Explication pour l oral

Phrase possible:

> PostgreSQL contient le coeur metier de la plateforme SOC: utilisateurs, incidents et chronologie. Elasticsearch joue le role de stockage NoSQL pour les evenements techniques et les traces d audit. Les deux stockages sont consultables depuis la vue Donnees de SOCket. Suricata produit les alertes EVE JSON, puis SOCket les transforme en incidents exploitables par les analystes.
