from __future__ import annotations

import base64
import datetime as dt
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Any, Optional
from urllib import error, request

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
import psycopg2
from psycopg2.extras import Json, RealDictCursor

from detector import analyze_raw_logs


APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "dev-change-this-secret")
ACCESS_TOKEN_TTL_MINUTES = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "120"))
SENSOR_TOKEN = os.getenv("SENSOR_TOKEN", "dev-sensor-token")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX", "socket-events")

security = HTTPBearer(auto_error=False)

app = FastAPI(
    title="SOCket API",
    description="API back-end pour la plateforme SOC et IDS SOCket",
    version="2.0.0",
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=1, max_length=200)


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = ""
    source_ip: str = Field(default="unknown", max_length=64)
    severity: str = Field(default="Medium", pattern="^(Low|Medium|High|Critical)$")
    attack_type: str = Field(default="Manual", max_length=80)
    score: int = Field(default=40, ge=0, le=100)
    confidence: int = Field(default=60, ge=0, le=100)
    recommendation: str = ""
    evidence: list[str] = Field(default_factory=list)
    assigned_to: Optional[int] = None


class IncidentUpdate(BaseModel):
    status: Optional[str] = Field(default=None, pattern="^(Nouveau|En cours|Résolu|Clos)$")
    severity: Optional[str] = Field(default=None, pattern="^(Low|Medium|High|Critical)$")
    assigned_to: Optional[int] = None
    recommendation: Optional[str] = None


class CommentCreate(BaseModel):
    message: str = Field(min_length=2, max_length=1000)


class RawLogPayload(BaseModel):
    raw_logs: str = Field(min_length=1)


class AlertIngest(BaseModel):
    title: str
    description: str = ""
    source_ip: str = "unknown"
    severity: str = "Medium"
    attack_type: str = "External Alert"
    score: int = 50
    confidence: int = 70
    recommendation: str = ""
    evidence: list[str] = Field(default_factory=list)


def db_config() -> dict[str, Any]:
    return {
        "host": os.getenv("POSTGRES_HOST", "db-sql"),
        "port": int(os.getenv("POSTGRES_PORT", "5432")),
        "dbname": os.getenv("POSTGRES_DB", "socket_db"),
        "user": os.getenv("POSTGRES_USER", "admin"),
        "password": os.getenv("POSTGRES_PASSWORD", "StrongPassword123!"),
    }


def get_conn():
    return psycopg2.connect(**db_config(), cursor_factory=RealDictCursor)


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    iterations = 260_000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), iterations)
    return f"pbkdf2_sha256${iterations}${salt}${base64.b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algorithm, iterations, salt, digest = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(base64.b64decode(digest), candidate)
    except Exception:
        return False


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def sign_token(unsigned: str) -> str:
    return b64url(hmac.new(APP_SECRET_KEY.encode(), unsigned.encode(), hashlib.sha256).digest())


def create_access_token(user: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "sub": str(user["id"]),
        "username": user["username"],
        "role": user["role"],
        "exp": int((utcnow() + dt.timedelta(minutes=ACCESS_TOKEN_TTL_MINUTES)).timestamp()),
    }
    unsigned = (
        f"{b64url(json.dumps(header, separators=(',', ':')).encode())}."
        f"{b64url(json.dumps(payload, separators=(',', ':')).encode())}"
    )
    return f"{unsigned}.{sign_token(unsigned)}"


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        header_b64, payload_b64, signature = token.split(".", 2)
        unsigned = f"{header_b64}.{payload_b64}"
        if not hmac.compare_digest(sign_token(unsigned), signature):
            raise ValueError("bad signature")
        payload = json.loads(b64url_decode(payload_b64))
        if int(payload["exp"]) < int(utcnow().timestamp()):
            raise ValueError("expired")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide") from exc


def current_user(credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentification requise")
    payload = decode_access_token(credentials.credentials)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, username, role FROM users WHERE id = %s", (payload["sub"],))
        user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    return dict(user)


def require_sensor(x_socket_sensor_token: str = Header(default="")) -> None:
    if not SENSOR_TOKEN or not hmac.compare_digest(x_socket_sensor_token, SENSOR_TOKEN):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Jeton capteur invalide")


def ensure_schema() -> None:
    for attempt in range(30):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        role VARCHAR(20) NOT NULL DEFAULT 'analyst',
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP")
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS incidents (
                        id SERIAL PRIMARY KEY,
                        title VARCHAR(180) NOT NULL,
                        description TEXT DEFAULT '',
                        severity VARCHAR(10) DEFAULT 'Medium',
                        status VARCHAR(20) DEFAULT 'Nouveau',
                        assigned_to INTEGER REFERENCES users(id),
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                for column_sql in (
                    "ALTER TABLE incidents ADD COLUMN IF NOT EXISTS source_ip VARCHAR(64) DEFAULT 'unknown'",
                    "ALTER TABLE incidents ADD COLUMN IF NOT EXISTS attack_type VARCHAR(80) DEFAULT 'Manual'",
                    "ALTER TABLE incidents ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0",
                    "ALTER TABLE incidents ADD COLUMN IF NOT EXISTS confidence INTEGER DEFAULT 0",
                    "ALTER TABLE incidents ADD COLUMN IF NOT EXISTS recommendation TEXT DEFAULT ''",
                    "ALTER TABLE incidents ADD COLUMN IF NOT EXISTS evidence JSONB DEFAULT '[]'::jsonb",
                ):
                    cur.execute(column_sql)
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS incident_events (
                        id SERIAL PRIMARY KEY,
                        incident_id INTEGER NOT NULL REFERENCES incidents(id) ON DELETE CASCADE,
                        actor VARCHAR(80) NOT NULL,
                        event_type VARCHAR(40) NOT NULL,
                        message TEXT NOT NULL,
                        created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                seed_users(cur)
                seed_incident(cur)
                conn.commit()
            ensure_elastic_index()
            return
        except psycopg2.OperationalError:
            if attempt == 29:
                raise
            time.sleep(2)


def seed_users(cur) -> None:
    users = (
        ("admin", hash_password(os.getenv("SOCKET_ADMIN_PASSWORD", "Admin123!")), "admin"),
        ("analyst", hash_password(os.getenv("SOCKET_ANALYST_PASSWORD", "Analyst123!")), "analyst"),
    )
    for username, password_hash, role in users:
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s) ON CONFLICT (username) DO NOTHING",
            (username, password_hash, role),
        )


def seed_incident(cur) -> None:
    cur.execute("SELECT COUNT(*) AS count FROM incidents")
    if int(cur.fetchone()["count"]) > 0:
        return
    cur.execute(
        """
        INSERT INTO incidents
            (title, description, source_ip, severity, status, attack_type, score, confidence, recommendation, evidence)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """,
        (
            "Scan de ports detecte (Nmap)",
            "Incident initial de demonstration cree au demarrage de SOCket.",
            "10.0.0.5",
            "Low",
            "Résolu",
            "Port Scan",
            28,
            70,
            "Conserver la trace et confirmer que seuls les ports attendus sont exposes.",
            Json(["Nmap SYN scan detecte sur le segment interne"]),
        ),
    )
    incident_id = cur.fetchone()["id"]
    add_event(cur, incident_id, "system", "creation", "Incident de demonstration initialise.")


def elastic_auth_header() -> str:
    user = os.getenv("ELASTIC_USER", "elastic")
    password = os.getenv("ELASTIC_PASSWORD", "StrongElasticPass123!")
    return "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()


def elastic_request(method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any] | None:
    base_url = os.getenv("ELASTIC_URL", "http://db-nosql:9200").rstrip("/")
    data = None if payload is None else json.dumps(payload).encode()
    req = request.Request(f"{base_url}{path}", data=data, method=method)
    req.add_header("Authorization", elastic_auth_header())
    req.add_header("Content-Type", "application/json")
    try:
        with request.urlopen(req, timeout=2) as response:
            return json.loads(response.read().decode() or "{}")
    except (error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def ensure_elastic_index() -> None:
    mapping = {
        "mappings": {
            "properties": {
                "timestamp": {"type": "date"},
                "event_type": {"type": "keyword"},
                "actor": {"type": "keyword"},
                "source_ip": {"type": "ip"},
                "severity": {"type": "keyword"},
                "message": {"type": "text"},
            }
        }
    }
    elastic_request("PUT", f"/{ELASTIC_INDEX}", mapping)


def log_security_event(event_type: str, message: str, actor: str = "system", **extra: Any) -> None:
    document = {
        "timestamp": utcnow().isoformat(),
        "event_type": event_type,
        "actor": actor,
        "message": message,
        **extra,
    }
    elastic_request("POST", f"/{ELASTIC_INDEX}/_doc", document)


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    for key in ("created_at", "updated_at"):
        value = item.get(key)
        if isinstance(value, dt.datetime):
            item[key] = value.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(item.get("evidence"), str):
        try:
            item["evidence"] = json.loads(item["evidence"])
        except json.JSONDecodeError:
            item["evidence"] = []
    item["evidence"] = item.get("evidence") or []
    return item


def add_event(cur, incident_id: int, actor: str, event_type: str, message: str) -> None:
    cur.execute(
        "INSERT INTO incident_events (incident_id, actor, event_type, message) VALUES (%s, %s, %s, %s)",
        (incident_id, actor, event_type, message),
    )


def create_incident_record(cur, incident: IncidentCreate | AlertIngest, actor: str) -> dict[str, Any]:
    cur.execute(
        """
        INSERT INTO incidents
            (title, description, source_ip, severity, status, attack_type, score, confidence, recommendation, evidence, assigned_to)
        VALUES (%s, %s, %s, %s, 'Nouveau', %s, %s, %s, %s, %s, %s)
        RETURNING *
        """,
        (
            incident.title,
            incident.description,
            incident.source_ip,
            incident.severity,
            incident.attack_type,
            incident.score,
            incident.confidence,
            incident.recommendation,
            Json(incident.evidence),
            getattr(incident, "assigned_to", None),
        ),
    )
    row = cur.fetchone()
    add_event(cur, row["id"], actor, "creation", f"Incident cree: {incident.attack_type}")
    log_security_event(
        "incident.created",
        incident.title,
        actor=actor,
        source_ip=incident.source_ip,
        severity=incident.severity,
        incident_id=row["id"],
        attack_type=incident.attack_type,
        score=incident.score,
    )
    return normalize_row(row)


@app.on_event("startup")
def on_startup() -> None:
    ensure_schema()


@app.get("/")
def read_root():
    return {"status": "ok", "message": "API SOCket operationnelle.", "version": app.version}


@app.post("/api/v1/auth/login")
@app.post("/v1/auth/login")
def login(payload: LoginRequest):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, username, password_hash, role FROM users WHERE username = %s", (payload.username,))
        user = cur.fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            log_security_event("auth.failed", f"Echec de connexion pour {payload.username}", actor=payload.username)
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identifiants invalides")
        token = create_access_token(user)
        log_security_event("auth.success", f"Connexion de {user['username']}", actor=user["username"])
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": ACCESS_TOKEN_TTL_MINUTES * 60,
            "user": {"id": user["id"], "username": user["username"], "role": user["role"]},
        }


@app.get("/api/v1/me")
@app.get("/v1/me")
def me(user: dict[str, Any] = Depends(current_user)):
    return user


@app.get("/api/v1/users")
@app.get("/v1/users")
def list_users(user: dict[str, Any] = Depends(current_user)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, username, role FROM users ORDER BY username")
        return cur.fetchall()


@app.get("/api/v1/database/preview")
@app.get("/v1/database/preview")
def database_preview(user: dict[str, Any] = Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces reserve aux administrateurs")
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id, username, role, created_at FROM users ORDER BY id")
        users = [normalize_row(row) for row in cur.fetchall()]
        cur.execute(
            """
            SELECT id, title, source_ip, attack_type, severity, score, status, created_at, updated_at
            FROM incidents
            ORDER BY created_at DESC, id DESC
            LIMIT 50
            """
        )
        incidents = [normalize_row(row) for row in cur.fetchall()]
        cur.execute(
            """
            SELECT id, incident_id, actor, event_type, message, created_at
            FROM incident_events
            ORDER BY created_at DESC, id DESC
            LIMIT 50
            """
        )
        events = [normalize_row(row) for row in cur.fetchall()]
    return {
        "postgresql": {
            "users": users,
            "incidents": incidents,
            "incident_events": events,
        },
        "elasticsearch": {
            "index": ELASTIC_INDEX,
        },
    }


@app.get("/api/v1/incidents")
@app.get("/v1/incidents")
def get_incidents(
    user: dict[str, Any] = Depends(current_user),
    severity: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    q: Optional[str] = Query(default=None),
):
    clauses = []
    params: list[Any] = []
    if severity:
        clauses.append("i.severity = %s")
        params.append(severity)
    if status_filter:
        clauses.append("i.status = %s")
        params.append(status_filter)
    if q:
        clauses.append("(i.title ILIKE %s OR i.description ILIKE %s OR i.source_ip ILIKE %s)")
        params.extend([f"%{q}%", f"%{q}%", f"%{q}%"])
    where = "WHERE " + " AND ".join(clauses) if clauses else ""
    query = f"""
        SELECT i.*, u.username AS assigned_username
        FROM incidents i
        LEFT JOIN users u ON u.id = i.assigned_to
        {where}
        ORDER BY i.created_at DESC, i.id DESC
        LIMIT 200
    """
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return [normalize_row(row) for row in cur.fetchall()]


@app.get("/api/v1/incidents/{incident_id}")
@app.get("/v1/incidents/{incident_id}")
def get_incident(incident_id: int, user: dict[str, Any] = Depends(current_user)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            SELECT i.*, u.username AS assigned_username
            FROM incidents i
            LEFT JOIN users u ON u.id = i.assigned_to
            WHERE i.id = %s
            """,
            (incident_id,),
        )
        incident = cur.fetchone()
        if not incident:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident introuvable")
        cur.execute("SELECT * FROM incident_events WHERE incident_id = %s ORDER BY created_at DESC, id DESC", (incident_id,))
        item = normalize_row(incident)
        item["events"] = [normalize_row(event) for event in cur.fetchall()]
        return item


@app.post("/api/v1/incidents", status_code=status.HTTP_201_CREATED)
@app.post("/v1/incidents", status_code=status.HTTP_201_CREATED)
def create_incident(incident: IncidentCreate, user: dict[str, Any] = Depends(current_user)):
    with get_conn() as conn, conn.cursor() as cur:
        created = create_incident_record(cur, incident, user["username"])
        conn.commit()
        return created


@app.patch("/api/v1/incidents/{incident_id}")
@app.patch("/v1/incidents/{incident_id}")
def update_incident(incident_id: int, payload: IncidentUpdate, user: dict[str, Any] = Depends(current_user)):
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aucune modification")
    set_clauses = []
    params: list[Any] = []
    for key, value in updates.items():
        set_clauses.append(f"{key} = %s")
        params.append(value)
    set_clauses.append("updated_at = CURRENT_TIMESTAMP")
    params.append(incident_id)
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(f"UPDATE incidents SET {', '.join(set_clauses)} WHERE id = %s RETURNING *", params)
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident introuvable")
        add_event(cur, incident_id, user["username"], "update", f"Mise a jour: {', '.join(updates.keys())}")
        conn.commit()
        log_security_event("incident.updated", f"Incident #{incident_id} mis a jour", actor=user["username"], incident_id=incident_id)
        return normalize_row(row)


@app.post("/api/v1/incidents/{incident_id}/comments", status_code=status.HTTP_201_CREATED)
@app.post("/v1/incidents/{incident_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(incident_id: int, payload: CommentCreate, user: dict[str, Any] = Depends(current_user)):
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute("SELECT id FROM incidents WHERE id = %s", (incident_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Incident introuvable")
        add_event(cur, incident_id, user["username"], "comment", payload.message)
        conn.commit()
        log_security_event("incident.comment", f"Commentaire sur incident #{incident_id}", actor=user["username"], incident_id=incident_id)
    return {"message": "Commentaire ajoute"}


@app.post("/api/v1/detections/analyze")
@app.post("/v1/detections/analyze")
def analyze_logs(payload: RawLogPayload, user: dict[str, Any] = Depends(current_user)):
    detections = analyze_raw_logs(payload.raw_logs)
    log_security_event("ids.analysis", f"{len(detections)} detection(s) produite(s)", actor=user["username"])
    return {"detections": detections, "count": len(detections)}


@app.post("/api/v1/ingest/alert", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_sensor)])
@app.post("/v1/ingest/alert", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_sensor)])
def ingest_alert(alert: AlertIngest):
    with get_conn() as conn, conn.cursor() as cur:
        created = create_incident_record(cur, alert, "ids-sensor")
        conn.commit()
        return created


@app.post("/api/v1/ingest/nginx-logs", dependencies=[Depends(require_sensor)])
@app.post("/v1/ingest/nginx-logs", dependencies=[Depends(require_sensor)])
def ingest_nginx_logs(payload: RawLogPayload):
    detections = analyze_raw_logs(payload.raw_logs)
    created = []
    with get_conn() as conn, conn.cursor() as cur:
        for detection in detections:
            created.append(create_incident_record(cur, AlertIngest(**detection), "ids-sensor"))
        conn.commit()
    return {"created": created, "detections": detections, "count": len(created)}


@app.get("/api/v1/logs/recent")
@app.get("/v1/logs/recent")
def recent_logs(user: dict[str, Any] = Depends(current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acces reserve aux administrateurs")
    result = elastic_request(
        "POST",
        f"/{ELASTIC_INDEX}/_search",
        {"size": 25, "sort": [{"timestamp": {"order": "desc"}}], "query": {"match_all": {}}},
    )
    hits = ((result or {}).get("hits") or {}).get("hits") or []
    return [hit.get("_source", {}) for hit in hits]
