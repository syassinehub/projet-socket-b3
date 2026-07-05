# Rapport d incident de securite - SOCket

**ID:** INC-IDS-DEMO-001  
**Date:** 2026-07-01  
**Statut:** Mitige  
**Severite:** Haute a critique selon le score IDS

## Resume executif

Une simulation multi-vecteurs a ete lancee contre le reverse proxy SOCket. Les logs Nginx ont ete collectes puis analyses par le moteur IDS SOCket. Les detections ont produit des incidents classes par type d attaque, score de dangerosite et niveau de confiance.

Impact estime:

- exposition potentielle de chemins sensibles;
- tentative d injection SQL;
- tentative de bruteforce;
- reconnaissance de surface d administration;
- bruit reseau anormal lie a la reconnaissance.

## Observations techniques

Exemples de vecteurs analyses:

- Recherche de fichiers sensibles: `/.env`, `/config.php`, `/backup.zip`.
- Reconnaissance de surfaces admin: `/admin`, `/wp-admin`, `/phpmyadmin`.
- Injection SQL: payload `UNION SELECT` et condition `OR 1=1`.
- Bruteforce: echecs repetes sur `/api/v1/auth/login`.
- Traversal: tentative d acces a `/../../etc/passwd`.

## Qualification SOC

| Element | Valeur |
| --- | --- |
| Source principale | Logs Nginx |
| Detection | Moteur IDS interne SOCket |
| Donnees metier | PostgreSQL |
| Journalisation | Elasticsearch |
| Type d incident | Multi-vecteurs web |
| Confiance | Moyenne a elevee selon les preuves |

## Preuves attendues

Dans le dashboard SOCket:

- titre de l incident;
- IP source;
- score;
- severite;
- preuve HTTP;
- recommandation;
- chronologie.

Dans PostgreSQL:

```sql
SELECT id, title, attack_type, severity, score, status
FROM incidents
ORDER BY created_at DESC
LIMIT 5;
```

Dans Elasticsearch:

```bash
curl -s http://localhost/api/v1/logs/recent
```

## Reponse et mitigation

- Nginx applique des en-tetes de securite et du rate limiting.
- Les chemins sensibles retournent 404.
- Les detections creent automatiquement des incidents dans SOCket.
- Les actions analystes sont tracees dans la chronologie incident.
- Les evenements applicatifs sont journalises dans Elasticsearch.

## Actions analyste recommandees

1. Confirmer les IP sources et les horodatages.
2. Verifier si les attaques ont touche des endpoints sensibles.
3. Passer les incidents critiques en statut `En cours`.
4. Assigner l incident a un analyste.
5. Ajouter un commentaire d investigation.
6. Appliquer ou confirmer les mitigations.
7. Cloturer l incident quand les preuves sont analysees.

## Ameliorations futures

- Brancher Suricata ou Wazuh pour completer le moteur IDS interne.
- Ajouter HTTPS avec certificats.
- Ajouter une politique de verrouillage de compte apres trop d echecs.
- Ajouter des playbooks de reponse par type d attaque.
