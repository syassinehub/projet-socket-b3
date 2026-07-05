# Specifications du projet SOCket

## 1. Contexte

SOCket repond au theme SOC/CSIRT de l enonce: fournir une plateforme centralisee permettant a une equipe securite de detecter, qualifier, suivre et documenter des incidents.

Le prototype est volontairement oriente demonstration pedagogique. Il montre les briques attendues dans un projet cyber B3:

- application web;
- API securisee;
- base SQL;
- base NoSQL;
- journalisation;
- detection d attaques;
- gestion d incidents;
- hardening;
- audit/pentest;
- PCA/PRA;
- documentation.

## 2. Besoins fonctionnels couverts

- Authentification des analystes et administrateurs.
- Tableau de bord centralise des incidents.
- Creation automatique d incidents par capteur IDS.
- Qualification par severite, score, confiance, type d attaque et IP source.
- Mise a jour du statut: Nouveau, En cours, Resolu, Clos.
- Assignation d un incident a un analyste.
- Commentaires et chronologie d investigation.
- Conservation de preuves techniques issues des alertes Suricata EVE JSON.
- Consultation des evenements de securite stockes dans Elasticsearch.

## 3. Architecture technique

- Frontend: Vue.js compile en build statique.
- Backend: FastAPI expose une API REST securisee.
- SQL: PostgreSQL stocke utilisateurs, roles, incidents et evenements.
- NoSQL: Elasticsearch stocke les journaux de securite et evenements applicatifs.
- Reverse proxy: Nginx centralise l exposition publique et applique les en-tetes de securite.
- IDS: Suricata detecte les attaques et SOCket ingere les alertes EVE JSON avec classification et scoring.
- DevOps: Docker Compose et GitHub Actions.

Voir le schema complet dans `docs/architecture.md`.

## 4. Security by design

- Secrets sortis du `docker-compose.yml` et charges via `.env`.
- Token d authentification pour les utilisateurs.
- Token capteur separe pour l ingestion IDS.
- Rate limiting Nginx sur API et authentification.
- Blocage des chemins sensibles comme `/.env`, `/.git`, `config.php`.
- Journalisation dans Elasticsearch pour audit et investigation.

## 5. Donnees gerees

### SQL

PostgreSQL stocke les donnees metier:

- comptes utilisateurs;
- roles;
- incidents;
- statut et assignation;
- chronologie d investigation.

### NoSQL

Elasticsearch stocke les evenements techniques:

- connexions;
- creations d incidents;
- modifications;
- evenements IDS;
- traces utiles a l audit.

## 6. Detection et classement

Suricata analyse le trafic et produit des alertes au format EVE JSON. SOCket lit ces alertes et les transforme en incidents. Chaque detection contient:

- un type d attaque;
- une IP source;
- un score de dangerosite;
- une severite;
- un niveau de confiance;
- une preuve;
- une recommandation.

Le score n est pas recopie directement depuis Suricata. SOCket part de la severite Suricata, puis ajuste le score avec:

- le type d attaque;
- le statut HTTP observe;
- la cible visee;
- la presence de preuves techniques;
- le niveau de precision de la signature.

Exemple: une alerte Suricata `severity=1` sert de base critique, mais SOCket peut renforcer ou reduire le score selon le contexte.

## 7. Limites du prototype

- Pas de HTTPS en local.
- RBAC simple.
- Elasticsearch sans interface Kibana.
- La capture live Suricata dans Docker/WSL peut demander des privileges reseau; un fichier EVE de demonstration est fourni.

## 8. Evolutions possibles

- Ajouter Wazuh.
- Ajouter Kibana.
- Ajouter HTTPS.
- Ajouter verrouillage de compte apres echecs repetes.
- Ajouter des playbooks par type d attaque.
- Ajouter un RBAC plus granulaire.
