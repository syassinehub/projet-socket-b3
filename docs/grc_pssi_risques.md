# Gouvernance et Sécurité (GRC) - Projet SOCket

## 1. Politique de Sécurité des Systèmes d'Information (PSSI)

La présente PSSI définit les règles de sécurité fondamentales pour la plateforme SOCket :
- **Contrôle d'accès :** Le principe du moindre privilège s'applique. Les analystes n'ont accès qu'aux fonctions nécessaires à la qualification des incidents.
- **Traçabilité :** Toutes les actions de modification sur les incidents de sécurité doivent être journalisées (logs) et stockées de manière immuable.
- **Protection des données :** Les mots de passe des utilisateurs doivent être hachés (ex: algorithme bcrypt). Les flux de communication (entre le front-end et l'API) doivent être chiffrés.
- **Résilience :** Une sauvegarde quotidienne de la base de données PostgreSQL doit être effectuée et testée (conformément au PCA/PRA).

## 2. Analyse de Risques (Méthodologie simplifiée inspirée d'EBIOS RM)

Pour justifier notre architecture "Security by Design", voici les risques majeurs identifiés et les mesures de traitement appliquées :

| Événement Redouté (Risque) | Gravité | Vraisemblance | Mesure de sécurité (Traitement) |
| :--- | :---: | :---: | :--- |
| **R1. Compromission d'un compte Analyste** (Vol d'identifiants permettant de modifier/clôturer de fausses alertes) | Critique | Moyenne | Mise en place de rôles stricts (RBAC) en BDD. Obligation de mots de passe complexes. |
| **R2. Exploitation d'une faille web** (ex: Injection SQL via l'interface du dashboard) | Élevée | Moyenne | Utilisation d'un framework moderne (Vue.js) pour éviter les XSS. Utilisation d'un ORM côté API (FastAPI) pour prévenir les injections SQL. |
| **R3. Déni de service (DoS) ou indisponibilité du SOC** | Élevée | Faible | Conteneurisation (Docker) pour relancer rapidement les services. Reverse proxy (Nginx) pour filtrer les requêtes illégitimes. |
| **R4. Perte des données d'incidents (Ransomware/Crash)** | Critique | Faible | Stratégie de sauvegarde automatisée (Dumps PostgreSQL réguliers). |
