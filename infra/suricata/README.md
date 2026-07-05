# Suricata SOCket

Suricata est utilise comme moteur de detection IDS. Il produit des evenements au format EVE JSON, puis SOCket les ingere avec l endpoint `/api/v1/ingest/suricata-eve`.

## Mode demo fiable

```bash
python3 infra/scripts/ingest_suricata_eve.py --sample
```

Ce mode envoie `infra/suricata/sample_eve.json` a l API. Il permet de montrer le flux Suricata meme si la capture reseau Docker/WSL n est pas disponible pendant la soutenance.

## Mode Suricata Docker

```bash
docker compose --profile suricata up -d ids-suricata
bash pentest/simulate_attack.sh
python3 infra/scripts/ingest_suricata_eve.py
```

Les alertes live sont lues depuis `infra/suricata/logs/eve.json`. Si ce fichier est vide ou absent, le script bascule sur le fichier de demonstration.
