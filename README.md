# SOCket - Plateforme SOC B3 Cyber

SOCket est une plateforme SOC/CSIRT de demonstration permettant de detecter, centraliser, qualifier et suivre des incidents de securite.

Le projet couvre:

- une interface web SOC;
- une API securisee;
- une base SQL PostgreSQL;
- une base NoSQL Elasticsearch;
- un reverse proxy Nginx durci;
- un IDS Suricata avec ingestion EVE JSON;
- des scripts de simulation d attaques;
- une procedure PCA/PRA;
- une documentation de soutenance.

## Lancement rapide

```bash
cp .env.example .env
docker compose up -d --build
```

Acces: http://localhost

Comptes de demonstration:

- `admin` / `Admin123!`
- `analyst` / `Analyst123!`

Les mots de passe sont parametrables dans `.env`:

- `admin` / `SOCKET_ADMIN_PASSWORD`
- `analyst` / `SOCKET_ANALYST_PASSWORD`

## Verification rapide

```bash
docker compose ps
curl -s -i http://localhost/api/v1/incidents | sed -n '1,40p'
```

Le endpoint `/api/v1/incidents` doit repondre `401 Unauthorized` sans token. C est normal: cela confirme que l API fonctionne et exige une authentification.

## Detection IDS et simulations

Suricata joue le role de moteur IDS. Il produit des alertes au format EVE JSON, puis SOCket les ingere avec `infra/scripts/ingest_suricata_eve.py`, classe les alertes, calcule un score de dangerosite et cree automatiquement des incidents.

```bash
bash pentest/simulate_attack.sh
bash pentest/attack_web_vectors.sh
bash pentest/attack_sqli.sh
bash pentest/attack_bruteforce.sh
```

Activer Suricata en mode Docker optionnel:

```bash
docker compose --profile suricata up -d ids-suricata
```

Ingerer un fichier EVE de demonstration fiable:

```bash
python3 infra/scripts/ingest_suricata_eve.py --sample
```

Les alertes Suricata couvrent notamment:

- SQL injection;
- XSS;
- directory traversal;
- command injection;
- SSRF;
- exposition de fichiers sensibles;
- decouverte de surfaces admin;
- bruteforce d authentification;
- reconnaissance HTTP.

SOCket calcule ensuite un score SOC a partir de la severite Suricata, du type d attaque, du statut HTTP, de la cible visee et des preuves disponibles.

## Briques principales

- Frontend Vue build statique servi par Nginx.
- API FastAPI avec authentification, JWT HMAC, RBAC simple et workflow incident.
- PostgreSQL pour les utilisateurs, incidents et chronologie.
- Elasticsearch pour les journaux de securite.
- Nginx reverse proxy avec en-tetes de securite, rate limiting et blocage de chemins sensibles.
- Suricata pour la detection IDS et le format EVE JSON.
- Sauvegarde PRA via `infra/scripts/backup_pra.sh`.
- CI GitHub Actions avec build frontend, verification Python et scan Trivy.

## Couverture de l enonce

| Livrable demande | Element fourni |
| --- | --- |
| Documentation fonctionnelle et technique | Dossier `docs/`, README, specifications, architecture, GRC, PRA et tests |
| Depot Git | Code applicatif, infrastructure Docker, scripts, documentation et CI versionnes |
| Plateforme SOC fonctionnelle et deployee | Stack Docker Compose accessible sur `http://localhost` avec frontend, API, PostgreSQL, Elasticsearch, Nginx et ingestion Suricata |

## Documentation

La documentation finale se trouve dans `docs/`. Elle couvre les livrables demandes: documentation fonctionnelle, documentation technique, securite/GRC, tests et aide pour l oral.

| Fichier | Role |
| --- | --- |
| `docs/installation.md` | Installation, lancement, acces et depannage |
| `docs/architecture.md` | Architecture technique et flux de donnees |
| `docs/specifications.md` | Contexte, besoins et choix techniques |
| `docs/bdd_et_logs.md` | PostgreSQL, Elasticsearch et logs |
| `docs/grc_pssi_risques.md` | PSSI, risques, mesures de securite |
| `docs/pra_pca.md` | Sauvegarde, restauration et continuite |
| `docs/incident_report_001.md` | Exemple de rapport d incident |

## Commandes utiles

Voir les donnees en interface graphique:

```text
http://localhost -> menu Donnees
```

Voir les donnees SQL:

```bash
docker exec -it socket-postgres psql -U admin -d socket_db
```

Voir les logs Elasticsearch:

```bash
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! http://localhost:9200/_cat/indices?v
```

Faire une sauvegarde PRA:

```bash
bash infra/scripts/backup_pra.sh
```

Arreter le projet sans supprimer les donnees:

```bash
docker compose down
```

## Limites et evolutions

- HTTPS n est pas active dans ce prototype local.
- La capture Suricata live dans Docker/WSL peut dependre des privileges reseau; un fichier EVE de demonstration est fourni pour une soutenance fiable.
- Le RBAC peut etre enrichi avec des permissions plus fines.
- Kibana ou Wazuh peuvent etre ajoutes comme evolution.
