# Spécifications Fonctionnelles et Techniques - Projet SOCket

## 1. Contexte et Objectifs
Actuellement, les équipes de sécurité (SOC, CSIRT) gèrent les événements via des outils éclatés (emails, tableurs, systèmes de ticketing génériques). Ce manque de centralisation ralentit la résolution des incidents.
L'objectif est de déployer un prototype fonctionnel d'une plateforme centralisée pour remplacer ces processus manuels.

## 2. Besoins Fonctionnels (Brief Client)
La plateforme SOCket doit permettre aux analystes de :
* Suivre un incident de sa détection à sa résolution.
* Collaborer efficacement entre les membres de l'équipe (CSIRT/SOC).
* Capitaliser sur les connaissances acquises pour anticiper les attaques.

## 3. Besoins Techniques (Security by Design)
* **Frontend** : Application web avec un dashboard interactif.
* **Backend** : API robuste avec durcissement de l'infrastructure.
* **Bases de données** : 
  * SQL pour la gestion des utilisateurs et le contrôle d'accès (DCL).
  * NoSQL pour la gestion des logs.
* **Déploiement** : Conteneurisation de l'application.