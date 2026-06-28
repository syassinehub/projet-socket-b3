# 🚨 Rapport d'Incident de Sécurité - SOCket

**ID de l'incident :** #INC-2026-06-28-001
**Date de détection :** 28 Juin 2026
**Analyste référent :** Yassine (Ingénieur Cyber / Administrateur SOC)
**Statut actuel :** Clos / Mitigé
**Sévérité :** Moyenne (Tentative d'intrusion non aboutie)

---

## 1. Résumé Exécutif (Executive Summary)
Le 28 Juin 2026, l'infrastructure de détection (Reverse Proxy Nginx) a intercepté une vague de requêtes HTTP suspectes ciblant le serveur web public. L'analyse comportementale indique une attaque automatisée combinant une tentative de **Déni de Service (DoS)** et de **Directory Fuzzing / Bruteforce** (recherche de répertoires cachés ou de fichiers de configuration sensibles). L'attaque a été contenue par la configuration architecturale actuelle sans aucun impact sur la confidentialité ou la disponibilité des données.

## 2. Chronologie de l'incident (Timeline)
*   **20:14:44 :** Début de l'attaque. L'adresse IP source commence à émettre de multiples requêtes HTTP GET automatisées.
*   **20:14:44 - 20:15:14 :** Phase de scan actif (Directory Bruteforce). Ciblage de fichiers d'administration et d'environnement.
*   **20:15:15 :** Fin de la vague d'attaque (arrêt du script malveillant).
*   **20:20:00 :** Début de l'analyse forensique par l'équipe SOC sur les journaux Nginx (`access.log`).

## 3. Analyse Forensique Détaillée (Preuves techniques)
L'extraction des logs depuis le conteneur `socket-nginx` (Reverse Proxy) a permis d'isoler le trafic malveillant du trafic légitime :

*   **Vecteur d'attaque :** Requêtes HTTP directes.
*   **IP Source de l'attaquant :** `172.19.0.1` (Passerelle du réseau virtuel Docker).
*   **Empreinte de l'outil (User-Agent) :** `curl/7.88.1` (Outil en ligne de commande souvent utilisé pour l'automatisation de scripts).
*   **Cibles (Payloads) :** Tentatives d'accès à des chemins critiques standards :
    *   `/admin` et `/wp-admin` (Recherche de panels d'administration)
    *   `/.env` et `/config.php` (Recherche d'identifiants et mots de passe)
    *   `/backup.zip` (Tentative d'exfiltration de données)
    *   `/api/v1/users` (Recherche de données personnelles)

**Analyse des codes de retour HTTP :**
*   L'API FastAPI (Back-end) a correctement renvoyé des erreurs `404 Not Found` pour les routes inexistantes, validant son étanchéité.
*   Le Front-end (Vue.js) a renvoyé des codes `200 OK` sur certaines requêtes (`/.env`). Il s'agit d'un comportement standard des applications "Single Page Application" (SPA) qui interceptent le routage, mais aucune donnée sensible n'a été divulguée (l'application ne possède pas ces fichiers).

*Extrait brut du log d'audit :*
> `172.19.0.1 - - [28/Jun/2026:20:14:44 +0000] "GET /admin HTTP/1.1" 200 415 "-" "curl/7.88.1" "-"`
> `172.19.0.1 - - [28/Jun/2026:20:14:44 +0000] "GET /.env HTTP/1.1" 200 415 "-" "curl/7.88.1" "-"`

## 4. Impact et Mesures de Mitigation Actuelles
**Impact estimé :** Nul. 
L'infrastructure conteneurisée sous Docker a parfaitement joué son rôle. Les principes de durcissement (Hardening) appliqués lors du déploiement ont bloqué la progression de l'attaquant :
1.  **Segmentation réseau :** Les conteneurs Web et API n'exposent aucun port public. Ils sont invisibles de l'extérieur.
2.  **Reverse Proxy :** Nginx a agi comme bouclier unique et a absorbé la charge.
3.  **En-têtes de sécurité :** Protections XSS et anti-Clickjacking actives.

## 5. Recommandations et Amélioration Continue
Pour renforcer notre posture de sécurité (Sécurité en profondeur) face à des attaques de plus grande envergure, les mesures suivantes sont préconisées pour le prochain cycle de développement :
1.  **Mise en place d'un Rate Limiting :** Configurer Nginx pour bloquer automatiquement une adresse IP effectuant plus de X requêtes par seconde.
2.  **Déploiement d'un WAF (Web Application Firewall) :** Intégrer ModSecurity pour analyser et bloquer les signatures d'attaques connues en temps réel.
3.  **Intégration SIEM :** Automatiser le transfert de ces logs Nginx vers la base Elasticsearch pour générer des alertes en temps réel sur le tableau de bord SOCket.