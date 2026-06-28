# Spécifications du Projet SOCket

## 1. Contexte
Dans un paysage de menaces en constante évolution, la gestion des événements de sécurité est souvent éclatée entre plusieurs outils non connectés (emails, tableurs, etc.), ce qui ralentit la résolution des incidents. Le RSSI d'un grand groupe industriel a mandaté notre équipe pour concevoir une plateforme centralisée et moderne permettant de suivre un incident de sa détection à sa résolution.

## 2. Besoins Fonctionnels
La plateforme (prototype fonctionnel) devra permettre aux analystes (SOC/CSIRT) de :
- S'authentifier de manière sécurisée (gestion des rôles : Analyste, Administrateur).
- Visualiser un tableau de bord centralisé regroupant les alertes de sécurité.
- Créer, lire, mettre à jour et clôturer des tickets d'incidents.
- Assigner des incidents à des membres spécifiques de l'équipe pour collaborer efficacement.
- Capitaliser sur les connaissances pour anticiper de futures attaques.

## 3. Besoins Techniques
Pour répondre au besoin de "Security by Design" et de durcissement, l'architecture retenue est la suivante :
- **Front-end :** Application web réactive développée en Vue.js.
- **Back-end :** API REST développée en Python avec le framework FastAPI.
- **Base de données relationnelle (SQL) :** PostgreSQL pour la gestion des utilisateurs, rôles (DCL) et tickets.
- **Base de données orientée documents (NoSQL) :** Elasticsearch pour l'ingestion, le stockage et la recherche rapide dans les logs de sécurité.
- **Infrastructure & Déploiement :** Conteneurisation complète avec Docker et Docker Compose. Reverse proxy Nginx pour la sécurité des flux.

## 4. Sécurité attendue
- Authentification et contrôle d'accès rigoureux.
- Infrastructure back-end durcie et segmentée.
- Politique de sauvegarde des bases de données.
- Intégration d'outils d'analyse dans un pipeline CI/CD.