# Gouvernance, PSSI et risques - SOCket

## 1. Objectif GRC

Cette documentation presente les choix de gouvernance et de securite appliques au projet SOCket. Elle montre que le projet ne se limite pas au developpement applicatif: il prend aussi en compte la protection des donnees, les risques, l audit, la continuite et la tracabilite.

## 2. PSSI projet

- Principe du moindre privilege pour les comptes applicatifs.
- Acces aux incidents reserve aux utilisateurs authentifies.
- Ingestion IDS reservee aux capteurs possedant le token dedie.
- Mots de passe stockes sous forme de hash PBKDF2-HMAC SHA-256 avec sel.
- Secrets applicatifs places dans `.env`, non versionnes.
- Journalisation des connexions, creations et modifications dans Elasticsearch.
- Sauvegarde PostgreSQL horodatee avec empreinte SHA256.

## 3. Regles de securite appliquees

| Domaine | Mesure |
| --- | --- |
| Authentification | Login obligatoire et jeton d acces |
| Mots de passe | Hash PBKDF2-HMAC SHA-256 avec sel |
| Secrets | `.env` ignore par Git |
| Exposition web | Reverse proxy Nginx unique |
| Hardening HTTP | En-tetes de securite et CSP |
| Anti-abus | Rate limiting Nginx sur API et login |
| Donnees sensibles | Blocage de chemins comme `/.env` et `/.git` |
| IDS | Token capteur dedie |
| Audit | Evenements dans Elasticsearch |
| PRA | Sauvegarde SQL et empreinte SHA256 |

## 4. Analyse de risques simplifiee

| Risque | Gravite | Vraisemblance | Mesures appliquees |
| --- | --- | --- | --- |
| Compromission compte analyste | Critique | Moyenne | Authentification, roles, logs, rotation possible du secret JWT |
| Injection ou attaque web | Elevee | Moyenne | FastAPI/Pydantic, reverse proxy, rate limiting, IDS sur logs |
| Exposition de secrets | Critique | Moyenne | `.env` ignore, blocage Nginx des chemins sensibles |
| Perte donnees incidents | Critique | Faible | Volume PostgreSQL persistant, script PRA, hash de sauvegarde |
| Indisponibilite plateforme SOC | Elevee | Faible | Conteneurisation, redemarrage automatique, services segmentes |
| Absence de traces forensic | Elevee | Moyenne | Chronologie incident, preuves IDS, index Elasticsearch |

## 5. PCA/PRA

Le PRA s appuie sur `infra/scripts/backup_pra.sh`, qui exporte PostgreSQL et genere une empreinte SHA256. La procedure complete est documentee dans `docs/pra_pca.md`.

## 6. Audit et pentest

Les scripts dans `pentest/` simulent des attaques controlees:

- `simulate_attack.sh`: scenario multi-vecteurs;
- `attack_sqli.sh`: injection SQL;
- `attack_bruteforce.sh`: bruteforce de connexion.

Ces scripts permettent de produire des logs, de tester l IDS et de generer des incidents exploitables dans le SOC.

## 7. Limites securite connues

- HTTPS absent en environnement local.
- Pas de politique de verrouillage de compte.
- Pas d authentification MFA.
- Pas de segmentation reseau avancee hors Docker.
- IDS interne plus simple qu un outil industriel.

Ces limites sont assumees pour un prototype local et sont listees comme ameliorations futures.
