# Scenario de demonstration - Soutenance SOCket

Ce scenario permet de presenter le projet de bout en bout pour l oral final: environ 25 minutes de presentation, puis 5 minutes de questions.

## 1. Introduire le besoin

Phrase possible:

> SOCket est une plateforme SOC/CSIRT de demonstration. Elle centralise les incidents, classe les alertes IDS, conserve les preuves techniques et permet a un analyste de suivre un incident jusqu a sa resolution.

Points a montrer:

- theme SOC/CSIRT respecte;
- gestion d incidents;
- detection et classification;
- base SQL et base NoSQL;
- hardening, logs, PRA et scripts d audit.

## 2. Lancer la plateforme

```bash
cd /home/yassine/projet-socket-b3
docker compose up -d
docker compose ps
```

Expliquer les services:

- `socket-nginx`: reverse proxy public;
- `socket-frontend`: interface;
- `socket-backend`: API;
- `socket-postgres`: SQL;
- `socket-elasticsearch`: NoSQL/logs.
- `socket-suricata`: IDS optionnel pour la capture live.

## 3. Se connecter au SOC

Ouvrir:

```text
http://localhost
```

Identifiants:

```text
admin / Admin123!
```

Montrer:

- tableau de bord;
- nombre d incidents;
- incidents critiques;
- score moyen;
- filtres de recherche.

## 4. Montrer le workflow incident

Selectionner un incident dans le tableau.

Montrer:

- type d attaque;
- IP source;
- score;
- severite;
- confiance;
- preuves;
- recommandation;
- changement de statut;
- assignation;
- commentaire d investigation;
- chronologie.

Phrase possible:

> Un incident n est pas seulement une ligne dans une table: il contient une preuve, une severite, une recommandation et une chronologie d actions analyste.

## 5. Simuler une attaque

Lancer:

```bash
bash pentest/simulate_attack.sh
bash pentest/attack_web_vectors.sh
```

Ce script genere des requetes suspectes:

- SQL injection;
- XSS;
- bruteforce;
- enumeration de chemins admin;
- tentative d acces a fichiers sensibles;
- directory traversal;
- command injection;
- SSRF;
- reconnaissance HTTP.

Revenir dans l interface et attendre quelques secondes. Le tableau des incidents se met a jour automatiquement grace au rafraichissement temps reel.

Montrer les nouveaux incidents.

## 6. Expliquer la detection

Phrase possible:

> Suricata joue le role d IDS. Il analyse le trafic du reverse proxy et produit des alertes au format EVE JSON. SOCket lit ces alertes, les transforme en incidents, puis ajoute un type d attaque, une severite, un score de dangerosite, un niveau de confiance, des preuves et une recommandation.

Score et severite:

- Suricata fournit une severite technique brute;
- SOCket calcule un score SOC avec le contexte de l alerte;
- le score final determine l affichage `Critical`, `High`, `Medium` ou `Low`.

Precision importante:

> En cas de probleme de capture live dans Docker/WSL, le projet fournit un fichier `infra/suricata/sample_eve.json`. Il garde le vrai format EVE JSON de Suricata pour rendre la demonstration fiable.

## 7. Montrer PostgreSQL

Dans l interface:

- cliquer sur `Donnees`;
- ouvrir l onglet `PostgreSQL`;
- montrer `users`, `incidents` et `incident_events`.

Verification possible en terminal:

```bash
docker exec -it socket-postgres psql -U admin -d socket_db
```

Dans `psql`:

```sql
\dt
SELECT id, username, role FROM users;
SELECT id, title, severity, status, attack_type, score FROM incidents ORDER BY created_at DESC LIMIT 5;
SELECT incident_id, actor, event_type, message FROM incident_events ORDER BY created_at DESC LIMIT 5;
\q
```

Phrase possible:

> PostgreSQL stocke la partie metier: utilisateurs, incidents, statuts, assignations et chronologie.

## 8. Montrer Elasticsearch

Dans l interface:

- cliquer sur `Donnees`;
- ouvrir l onglet `Elasticsearch`;
- montrer les derniers evenements de l index `socket-events`.

Verification possible en terminal:

```bash
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! http://localhost:9200/_cat/indices?v
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! "http://localhost:9200/socket-events/_search?pretty&size=5"
```

Phrase possible:

> Elasticsearch sert de base NoSQL pour les evenements techniques, utile pour l audit et l investigation.

## 9. Montrer le hardening

Tester le blocage d un fichier sensible:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost/.env
```

Resultat attendu:

```text
404
```

Expliquer:

- Nginx masque les chemins sensibles;
- Nginx applique des en-tetes de securite;
- l API est protegee par authentification;
- l ingestion IDS demande un token capteur;
- les secrets sont dans `.env`.

## 10. Montrer le PRA

```bash
bash infra/scripts/backup_pra.sh
ls -lh infra/backups
```

Phrase possible:

> Le PRA prevoit une sauvegarde SQL horodatee avec empreinte SHA256 pour verifier l integrite du dump.

## 11. Conclusion

Phrase possible:

> SOCket repond au besoin d une plateforme SOC pedagogique: detection Suricata, qualification, suivi, stockage SQL, logs NoSQL, hardening, audit, PRA et documentation. Les evolutions naturelles seraient HTTPS, Wazuh, Kibana et un RBAC plus granulaire.
