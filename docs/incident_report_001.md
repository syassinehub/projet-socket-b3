# Rapport d incident de securite - SOCket

**ID:** INC-IDS-DEMO-001  
**Date:** 2026-07-05  
**Statut:** Mitige  
**Severite:** Variable selon le score SOCket

## Resume executif

Une simulation multi-vecteurs a ete lancee contre le reverse proxy SOCket. Suricata a produit des alertes EVE JSON, puis SOCket les a ingerees pour creer des incidents classes par type d attaque, score de dangerosite et niveau de confiance.

Impact estime:

- exposition potentielle de chemins sensibles;
- tentative d injection SQL;
- tentative XSS;
- tentative de bruteforce;
- tentative de command injection;
- tentative SSRF;
- reconnaissance de surface d administration;
- bruit reseau anormal lie a la reconnaissance.

## Observations techniques

Exemples de vecteurs analyses:

- Recherche de fichiers sensibles: `/.env`, `/config.php`, `/backup.zip`.
- Reconnaissance de surfaces admin: `/admin`, `/wp-admin`, `/phpmyadmin`.
- Injection SQL: payload `UNION SELECT` et condition `OR 1=1`.
- XSS: payload `<script>alert(1)</script>`.
- Bruteforce: echecs repetes sur `/api/v1/auth/login`.
- Traversal: tentative d acces a `/../../etc/passwd`.
- Command injection: tentative via parametre `cmd=whoami`.
- SSRF: tentative d acces a `169.254.169.254`.

## Qualification SOC

| Element | Valeur |
| --- | --- |
| Source principale | Alertes Suricata EVE JSON |
| Detection | Suricata IDS |
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
docker exec socket-elasticsearch curl -s -u elastic:StrongElasticPass123! "http://localhost:9200/socket-events/_search?pretty&size=5"
```

## Reponse et mitigation

- Nginx applique des en-tetes de securite et du rate limiting.
- Les chemins sensibles retournent 404.
- Les alertes Suricata creent automatiquement des incidents dans SOCket.
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

- Ajouter Wazuh pour enrichir la detection et la supervision.
- Ajouter HTTPS avec certificats.
- Ajouter une politique de verrouillage de compte apres trop d echecs.
- Ajouter des playbooks de reponse par type d attaque.
