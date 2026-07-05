# Checklist finale de rendu - SOCket

## Avant de rendre le depot

- Le projet demarre avec `docker compose up -d --build`.
- Le fichier `.env` existe en local mais n est pas versionne.
- `.env.example` est versionne.
- Les conteneurs sont `Up`.
- PostgreSQL est `healthy`.
- Le login `admin / Admin123!` fonctionne.
- Le dashboard affiche les incidents.
- Les scripts de pentest generent de nouvelles alertes.
- Les incidents sont visibles dans PostgreSQL.
- Les evenements sont visibles dans Elasticsearch.
- Le script PRA cree une sauvegarde SQL et une empreinte SHA256.
- Les documents dans `docs/` sont presents et coherents.

## Verification technique rapide

```bash
cd /home/yassine/projet-socket-b3
docker compose up -d --build
docker compose ps
curl -s -i http://localhost/api/v1/incidents | sed -n '1,40p'
bash pentest/simulate_attack.sh
curl -s http://localhost/api/v1/logs/recent
bash infra/scripts/backup_pra.sh
```

## Documentation attendue

| Besoin | Document |
| --- | --- |
| Installation | `docs/installation.md` |
| Architecture | `docs/architecture.md` |
| Specifications | `docs/specifications.md` |
| Demo orale | `docs/demo_soutenance.md` |
| Tests | `docs/tests_validation.md` |
| SQL / NoSQL / logs | `docs/bdd_et_logs.md` |
| GRC / PSSI / risques | `docs/grc_pssi_risques.md` |
| PCA / PRA | `docs/pra_pca.md` |
| Rapport incident | `docs/incident_report_001.md` |
| Mapping enonce | `docs/evaluation_mapping.md` |
| Captures et preuves | `docs/captures_preuves.md` |

## Points a dire a l oral

- SOCket est une plateforme SOC/CSIRT.
- Les attaques simulees declenchent des alertes Suricata EVE JSON.
- SOCket transforme ces alertes en incidents.
- Les incidents sont classes par type, score, severite et confiance.
- PostgreSQL stocke les donnees metier.
- Elasticsearch stocke les evenements techniques.
- Nginx applique du hardening.
- Le PRA permet de sauvegarder la base SQL.
- Suricata est le moteur IDS presente pour la detection.

## Points a ne pas oublier

- Ne pas pousser `.env`.
- Ne pas supprimer les volumes avant la soutenance.
- Ne pas lancer `docker compose down -v` sauf si la perte de donnees est volontaire.
- Preparer les captures avant le rendu final.
- Tester la demo au moins une fois du debut a la fin.
