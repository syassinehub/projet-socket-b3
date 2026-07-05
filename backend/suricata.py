"""Suricata EVE JSON adapter for SOCket incidents."""
from __future__ import annotations

import json
from typing import Any, Iterable


SEVERITY_BASE = {
    1: ("Critical", 86, 72),
    2: ("High", 70, 66),
    3: ("Medium", 50, 58),
    4: ("Low", 30, 50),
}

RECOMMENDATIONS = {
    "SQL Injection": "Isoler la source, verifier les requetes SQL et confirmer que les entrees applicatives sont parametrees.",
    "Cross-Site Scripting": "Verifier l echappement des sorties, renforcer la CSP et controler les champs exposes.",
    "Directory Traversal": "Bloquer les chemins relatifs, verifier les routes exposees et conserver les preuves.",
    "Command Injection": "Isoler la source, verifier les commandes executees cote serveur et controler les journaux applicatifs.",
    "Credential Bruteforce": "Bloquer temporairement la source, verifier les comptes cibles et renforcer le rate limiting.",
    "Sensitive File Exposure": "Verifier qu aucun fichier sensible n est expose et confirmer les regles de blocage Nginx.",
    "Admin Surface Discovery": "Limiter l exposition des interfaces d administration et surveiller les scans repetes.",
    "SSRF": "Bloquer les acces aux adresses internes sensibles et verifier les fonctions de recuperation d URL.",
    "Reconnaissance": "Surveiller la source, limiter l enumeration et correler avec les logs Nginx.",
    "Malware": "Isoler l hote concerne, collecter les IOC et lancer une analyse antivirale.",
    "Policy Violation": "Verifier la regle de securite declenchee et documenter l ecart.",
    "Web Attack": "Analyser la requete HTTP, verifier le durcissement Nginx et conserver les preuves.",
    "Network Alert": "Qualifier l alerte Suricata, correler avec les flux reseau et prioriser selon la severite.",
}


def _as_events(raw_events: str) -> Iterable[dict[str, Any]]:
    raw_events = raw_events.strip()
    if not raw_events:
        return []
    if raw_events.startswith("["):
        try:
            data = json.loads(raw_events)
        except json.JSONDecodeError:
            return []
        return [item for item in data if isinstance(item, dict)]

    events: list[dict[str, Any]] = []
    for line in raw_events.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def _attack_type(signature: str, category: str) -> str:
    text = f"{signature} {category}".lower()
    if "ssrf" in text or "169.254.169.254" in text:
        return "SSRF"
    if "command injection" in text or "cmd=" in text or "remote code execution" in text or "whoami" in text:
        return "Command Injection"
    if "sql" in text or "injection" in text:
        return "SQL Injection"
    if "xss" in text or "cross-site" in text or "script" in text:
        return "Cross-Site Scripting"
    if "traversal" in text or "../" in text or "directory" in text:
        return "Directory Traversal"
    if "brute" in text or "credential" in text or "login" in text:
        return "Credential Bruteforce"
    if "sensitive" in text or "file exposure" in text or "information leak" in text:
        return "Sensitive File Exposure"
    if "admin" in text or "phpmyadmin" in text or "wp-admin" in text:
        return "Admin Surface Discovery"
    if "scan" in text or "recon" in text or "attempted information leak" in text:
        return "Reconnaissance"
    if "malware" in text or "trojan" in text or "cnc" in text:
        return "Malware"
    if "policy" in text:
        return "Policy Violation"
    if "web" in text or "http" in text:
        return "Web Attack"
    return "Network Alert"


def _suricata_level(alert: dict[str, Any]) -> int:
    try:
        return int(alert.get("severity", 4))
    except (TypeError, ValueError):
        return 4


def _severity_from_score(score: int) -> str:
    if score >= 85:
        return "Critical"
    if score >= 70:
        return "High"
    if score >= 45:
        return "Medium"
    return "Low"


def _clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


def _truncate(value: str, limit: int) -> str:
    return value if len(value) <= limit else f"{value[: limit - 3]}..."


def _http_evidence(event: dict[str, Any]) -> str | None:
    http = event.get("http") or {}
    if not isinstance(http, dict):
        return None
    method = http.get("http_method") or "HTTP"
    url = http.get("url") or http.get("hostname") or ""
    status = http.get("status")
    host = http.get("hostname")
    pieces = [str(method), str(url)]
    if status:
        pieces.append(f"status={status}")
    if host:
        pieces.append(f"host={host}")
    return " ".join(piece for piece in pieces if piece)


def _http_status(event: dict[str, Any]) -> int | None:
    http = event.get("http") or {}
    if not isinstance(http, dict):
        return None
    try:
        return int(http.get("status"))
    except (TypeError, ValueError):
        return None


def _http_url(event: dict[str, Any]) -> str:
    http = event.get("http") or {}
    if not isinstance(http, dict):
        return ""
    return str(http.get("url") or "").lower()


def _score_modifier(attack_type: str, category: str, event: dict[str, Any]) -> int:
    modifier = {
        "Malware": 12,
        "Command Injection": 10,
        "SQL Injection": 8,
        "SSRF": 7,
        "Directory Traversal": 6,
        "Credential Bruteforce": 5,
        "Sensitive File Exposure": 4,
        "Cross-Site Scripting": 3,
        "Admin Surface Discovery": 1,
        "Reconnaissance": -3,
        "Policy Violation": -2,
    }.get(attack_type, 0)

    category_text = category.lower()
    if "web application attack" in category_text:
        modifier += 3
    if "administrator" in category_text:
        modifier += 4
    if "information leak" in category_text:
        modifier += 2

    status_code = _http_status(event)
    if status_code is not None:
        if 200 <= status_code < 300:
            modifier += 4
        elif status_code in {401, 403}:
            modifier += 1
        elif status_code == 404:
            modifier -= 4
        elif status_code >= 500:
            modifier += 5

    url = _http_url(event)
    if any(token in url for token in ("/.env", "id_rsa", "passwd", "shadow", "config.php", "backup")):
        modifier += 5
    if any(token in url for token in ("whoami", "%7c", "%3b", ";", "|", "169.254.169.254")):
        modifier += 5
    if any(token in url for token in ("/admin", "/wp-admin", "/phpmyadmin", "/actuator", "/server-status")):
        modifier += 2
    if "/api/v1/auth/login" in url:
        modifier += 2

    return modifier


def _confidence_modifier(attack_type: str, event: dict[str, Any], alert: dict[str, Any]) -> int:
    modifier = 0
    if alert.get("signature_id"):
        modifier += 4
    if alert.get("category"):
        modifier += 3
    if _http_url(event):
        modifier += 4
    if event.get("timestamp"):
        modifier += 3
    if event.get("src_ip") and event.get("dest_ip") and event.get("proto"):
        modifier += 3

    status_code = _http_status(event)
    if status_code in {200, 201, 204}:
        modifier += 4
    elif status_code in {401, 403}:
        modifier += 2
    elif status_code == 404:
        modifier -= 3

    if attack_type in {"SQL Injection", "Directory Traversal", "Command Injection", "SSRF"}:
        modifier += 5
    elif attack_type in {"Sensitive File Exposure", "Credential Bruteforce"}:
        modifier += 4
    elif attack_type == "Reconnaissance":
        modifier -= 5

    return modifier


def _soc_scoring(event: dict[str, Any], alert: dict[str, Any], attack_type: str, category: str) -> tuple[str, int, int, str]:
    suricata_level = _suricata_level(alert)
    _, base_score, base_confidence = SEVERITY_BASE.get(suricata_level, SEVERITY_BASE[4])
    score_modifier = _score_modifier(attack_type, category, event)
    confidence_modifier = _confidence_modifier(attack_type, event, alert)
    score = _clamp(base_score + score_modifier)
    confidence = _clamp(base_confidence + confidence_modifier, 35, 98)
    severity = _severity_from_score(score)
    details = (
        f"scoring SOCket: severity_suricata={suricata_level}, "
        f"base_score={base_score}, contexte={score_modifier:+d}, "
        f"base_confiance={base_confidence}, preuves={confidence_modifier:+d}"
    )
    return severity, score, confidence, details


def _to_detection(event: dict[str, Any]) -> dict[str, Any] | None:
    if event.get("event_type") != "alert":
        return None
    alert = event.get("alert") or {}
    if not isinstance(alert, dict):
        return None

    signature = str(alert.get("signature") or "Alerte Suricata")
    category = str(alert.get("category") or "Non classe")
    attack_type = _attack_type(signature, category)
    severity, score, confidence, scoring_details = _soc_scoring(event, alert, attack_type, category)
    source_ip = str(event.get("src_ip") or "unknown")
    destination = str(event.get("dest_ip") or "unknown")
    proto = str(event.get("proto") or "unknown")
    src_port = event.get("src_port")
    dest_port = event.get("dest_port")
    sid = alert.get("signature_id")
    rev = alert.get("rev")

    evidence = [
        f"signature: {signature}",
        f"category: {category}",
        f"flow: {source_ip}:{src_port or '?'} -> {destination}:{dest_port or '?'} / {proto}",
    ]
    if sid:
        evidence.append(f"sid: {sid} rev: {rev or '?'} severity: {alert.get('severity', '?')}")
    http_line = _http_evidence(event)
    if http_line:
        evidence.append(f"http: {http_line}")
    if event.get("timestamp"):
        evidence.append(f"timestamp: {event['timestamp']}")
    evidence.append(scoring_details)

    return {
        "title": _truncate(f"Suricata: {signature}", 180),
        "description": (
            f"Suricata a detecte une alerte de categorie {category} "
            f"entre {source_ip} et {destination}."
        ),
        "source_ip": _truncate(source_ip, 64),
        "severity": severity,
        "attack_type": attack_type,
        "score": score,
        "confidence": confidence,
        "recommendation": RECOMMENDATIONS.get(attack_type, RECOMMENDATIONS["Network Alert"]),
        "evidence": evidence,
    }


def parse_suricata_eve(raw_events: str) -> list[dict[str, Any]]:
    detections: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for event in _as_events(raw_events):
        detection = _to_detection(event)
        if not detection:
            continue
        key = (
            detection["source_ip"],
            detection["title"],
            "|".join(detection["evidence"][:4]),
        )
        if key in seen:
            continue
        seen.add(key)
        detections.append(detection)
    return detections[:50]
