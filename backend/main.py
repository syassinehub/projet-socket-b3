from fastapi import FastAPI
from pydantic import BaseModel
import datetime

app = FastAPI(
    title="SOCket API",
    description="API back-end pour la plateforme de gestion d'incidents SOCket",
    version="1.0.0"
)

# Notre base de données en mémoire
db_incidents = [
    { "id": 1001, "date": "2026-06-28 10:00", "title": "Scan de ports détecté (Nmap)", "ip": "10.0.0.5", "severity": "Low", "status": "Résolu" }
]

# Modèle pour les alertes entrantes
class Incident(BaseModel):
    title: str
    ip: str
    severity: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API SOCket fonctionnelle."}

# Route GET : On supporte les deux chemins pour éviter le bug du Reverse Proxy
@app.get("/api/v1/incidents")
@app.get("/v1/incidents")
def get_incidents():
    return db_incidents[::-1]

# Route POST : On supporte les deux chemins pour l'injection d'alerte
@app.post("/api/v1/incidents")
@app.post("/v1/incidents")
def create_incident(incident: Incident):
    new_alert = {
        "id": 1001 + len(db_incidents),
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "title": incident.title,
        "ip": incident.ip,
        "severity": incident.severity,
        "status": "Nouveau"
    }
    db_incidents.append(new_alert)
    return {"message": "Alerte enregistrée avec succès"}