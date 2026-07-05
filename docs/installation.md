# Installation et lancement - SOCket

## Prerequis

- Debian ou WSL Debian.
- Docker et Docker Compose.
- Git.
- Python 3 pour lancer le capteur IDS local.

Verifier Docker:

```bash
docker --version
docker compose version
```

## Recuperer le projet

```bash
cd /home/yassine/projet-socket-b3
```

## Configurer les variables

Si le fichier `.env` n existe pas:

```bash
cp .env.example .env
```

Le fichier `.env` doit contenir au minimum:

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=StrongPassword123!
POSTGRES_DB=socket_db
ELASTIC_USER=elastic
ELASTIC_PASSWORD=StrongElasticPass123!
APP_SECRET_KEY=socket-local-demo-secret-change-before-prod
SENSOR_TOKEN=socket-local-sensor-token
SOCKET_ADMIN_PASSWORD=Admin123!
SOCKET_ANALYST_PASSWORD=Analyst123!
```

Important: `.env` contient des secrets et ne doit pas etre pousse sur Git.

## Demarrer la plateforme

```bash
docker compose up -d --build
```

Verifier l etat des conteneurs:

```bash
docker compose ps
```

Tous les services doivent etre `Up`, et PostgreSQL doit etre `healthy`.

## Acceder au SOC

URL:

```text
http://localhost
```

Comptes de demonstration:

```text
admin / Admin123!
analyst / Analyst123!
```

## Tests rapides apres lancement

Le frontend doit repondre:

```bash
curl -s -i http://localhost/ | sed -n '1,20p'
```

L API doit demander une authentification:

```bash
curl -s -i http://localhost/api/v1/incidents | sed -n '1,40p'
```

Resultat attendu:

```text
HTTP/1.1 401 Unauthorized
{"detail":"Authentification requise"}
```

## Probleme courant: 502 Bad Gateway

Un `502 Bad Gateway` indique que Nginx fonctionne mais que l API backend ne repond pas.

Commandes utiles:

```bash
docker compose ps
docker compose logs --tail=100 api
```

Si le message indique `password authentication failed for user "admin"`, le mot de passe PostgreSQL du volume Docker ne correspond plus au `.env`. Pour une demo locale, on peut realigner le mot de passe:

```bash
docker exec -u postgres socket-postgres psql -U admin -d socket_db -c "ALTER USER admin WITH PASSWORD 'StrongPassword123!'"
docker compose up -d --force-recreate api
```

## Arreter proprement

Arreter les conteneurs sans supprimer les donnees:

```bash
docker compose down
```

Attention: cette commande supprime aussi les volumes de base de donnees:

```bash
docker compose down -v
```
