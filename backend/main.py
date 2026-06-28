from fastapi import FastAPI

# Initialisation de l'API
app = FastAPI(
    title="SOCket API",
    description="API back-end pour la plateforme de gestion d'incidents SOCket",
    version="1.0.0"
)

# Route de test (Healthcheck)
@app.get("/")
def read_root():
    return {"status": "ok", "message": "L'API SOCket est fonctionnelle et sécurisée."}

# Route pour récupérer les alertes (simulées pour le moment)
@app.get("/api/v1/incidents")
def get_incidents():
    return [
        {"id": 1, "title": "Tentative de Bruteforce SSH", "severity": "High", "status": "Open"},
        {"id": 2, "title": "Connexion suspecte depuis IP étrangère", "severity": "Medium", "status": "Open"}
    ]