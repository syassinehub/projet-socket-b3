# Correspondance avec l enonce et la grille d evaluation

## Synthese

SOCket respecte le theme SOC/CSIRT en proposant une plateforme de detection, qualification, investigation et suivi d incidents. Le tableau ci-dessous relie les attentes du projet aux elements concrets presents dans le depot.

| Attente | Elements SOCket | Preuve / fichier |
| --- | --- |
| Plateforme fonctionnelle | Frontend Vue, API FastAPI, Docker Compose | `docker-compose.yml`, `frontend/`, `backend/` |
| Theme SOC/CSIRT | Dashboard incidents, workflow analyste, chronologie | `frontend/src/App.vue`, `backend/main.py` |
| Base SQL | PostgreSQL pour utilisateurs, incidents, evenements | `infra/postgres/init.sql`, `docs/bdd_et_logs.md` |
| Base NoSQL | Elasticsearch pour logs et evenements | `docker-compose.yml`, `docs/bdd_et_logs.md` |
| Detection d attaque | IDS interne sur logs Nginx | `backend/detector.py`, `infra/scripts/run_ids_scan.py` |
| Audit / pentest | Scripts SQLi, bruteforce et multi-vecteurs | `pentest/` |
| Hardening | Nginx security headers, rate limiting, blocage chemins sensibles | `infra/nginx/nginx.conf` |
| GRC / PSSI | Politique securite, risques, mesures | `docs/grc_pssi_risques.md` |
| PCA/PRA | Sauvegarde PostgreSQL et procedure restauration | `infra/scripts/backup_pra.sh`, `docs/pra_pca.md` |
| Investigation | Preuves, recommandations, commentaires, timeline | dashboard SOC, `incident_events` |
| Documentation | Installation, architecture, demo, tests, BDD/logs | `docs/` |
| DevOps | Build Docker, CI securite | `.github/workflows/security-audit.yml` |

## Demonstration conseillee

Pendant la soutenance, suivre `docs/demo_soutenance.md`:

1. lancer les conteneurs;
2. se connecter au SOC;
3. presenter un incident;
4. lancer une simulation d attaque;
5. verifier PostgreSQL;
6. verifier Elasticsearch;
7. montrer le hardening;
8. montrer la sauvegarde PRA.

## Points forts

- Le projet est coherent avec le theme SOC.
- Les incidents sont crees automatiquement depuis des logs reels.
- Les alertes sont qualifiees avec score, severite, confiance et preuves.
- La plateforme combine SQL et NoSQL.
- Les scripts permettent une demo reproductible.
- La documentation est structuree pour le rendu et l oral.

## Reste perfectible

- HTTPS n est pas active dans le prototype local.
- Le moteur IDS est base sur des regles internes; Suricata/Wazuh peut etre ajoute en extension.
- Le RBAC est volontairement simple pour rester lisible pendant la soutenance.
- Kibana n est pas integre, les logs Elasticsearch sont consultes par API/curl.
