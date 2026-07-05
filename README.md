# SOCket - Plateforme SOC B3 Cyber

SOCket est une plateforme SOC/CSIRT de demonstration permettant de detecter, centraliser, qualifier et suivre des incidents de securite.

Le projet couvre:

- une interface web SOC;
- une API securisee;
- une base SQL PostgreSQL;
- une base NoSQL Elasticsearch;
- un reverse proxy Nginx durci;
- un moteur IDS interne base sur l analyse de logs;
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

Les scripts dans `pentest/` generent de vrais logs HTTP via Nginx. Le script `infra/scripts/run_ids_scan.py` lit les logs, classe les attaques, calcule un score de dangerosite et cree automatiquement des incidents dans SOCket.

```bash
bash pentest/simulate_attack.sh
bash pentest/attack_sqli.sh
bash pentest/attack_bruteforce.sh
```

Le moteur IDS detecte notamment:

- SQL injection;
- XSS;
- directory traversal;
- exposition de fichiers sensibles;
- enumeration d interfaces admin;
- bruteforce d authentification;
- flood/reconnaissance HTTP.

## Briques principales

- Frontend Vue build statique servi par Nginx.
- API FastAPI avec authentification, JWT HMAC, RBAC simple et workflow incident.
- PostgreSQL pour les utilisateurs, incidents et chronologie.
- Elasticsearch pour les journaux de securite.
- Nginx reverse proxy avec en-tetes de securite, rate limiting et blocage de chemins sensibles.
- Sauvegarde PRA via `infra/scripts/backup_pra.sh`.
- CI GitHub Actions avec build frontend, verification Python et scan Trivy.

## Documentation

La documentation finale se trouve dans `docs/`:

| Fichier | Role |
| --- | --- |
| `docs/installation.md` | Installation, lancement, acces et depannage |
| `docs/architecture.md` | Architecture technique et flux de donnees |
| `docs/specifications.md` | Contexte, besoins et choix techniques |
| `docs/demo_soutenance.md` | Scenario complet pour la presentation orale |
| `docs/tests_validation.md` | Tests a executer avant le rendu |
| `docs/bdd_et_logs.md` | PostgreSQL, Elasticsearch et logs |
| `docs/grc_pssi_risques.md` | PSSI, risques, mesures de securite |
| `docs/pra_pca.md` | Sauvegarde, restauration et continuite |
| `docs/incident_report_001.md` | Exemple de rapport d incident |
| `docs/evaluation_mapping.md` | Correspondance avec les attentes de l enonce |
| `docs/checklist_rendu.md` | Checklist finale avant depot/soutenance |
| `docs/captures_preuves.md` | Captures et preuves conseillees |

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
curl -s http://localhost/api/v1/logs/recent
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
- Le moteur IDS est interne, pas base sur Suricata.
- Le RBAC peut etre enrichi avec des permissions plus fines.
- Kibana, Wazuh ou Suricata peuvent etre ajoutes comme evolution.
