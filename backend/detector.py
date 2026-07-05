"""Lightweight rule-based IDS engine for SOCket."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict, dataclass
import re
from typing import Iterable
from urllib.parse import unquote_plus


LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) '
    r'(?P<path>\S+) (?P<proto>[^"]+)" (?P<status>\d{3}) (?P<size>\S+) '
    r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
)

PATTERNS = [
    (
        "SQL Injection",
        re.compile(r"('|%27|\bor\b\s+1\s*=\s*1|union\s+select|sleep\s*\(|benchmark\s*\(|--|/\*)", re.I),
        92,
        90,
        "Bloquer la source, verifier les entrees applicatives et confirmer les requetes parametrees.",
    ),
    (
        "Cross-Site Scripting",
        re.compile(r"(<script|%3cscript|javascript:|onerror\s*=|onload\s*=|alert\s*\()", re.I),
        78,
        82,
        "Verifier l echappement en sortie, renforcer la CSP et controler les champs exposes.",
    ),
    (
        "Directory Traversal",
        re.compile(r"(\.\./|%2e%2e%2f|/etc/passwd|boot\.ini|win\.ini)", re.I),
        86,
        88,
        "Refuser les chemins relatifs, journaliser la tentative et verifier le routage.",
    ),
    (
        "Sensitive File Exposure",
        re.compile(r"(/\.env|/config\.php|/backup\.zip|/\.git|/id_rsa|/composer\.json)", re.I),
        72,
        80,
        "Retourner 404 sur les fichiers sensibles et verifier les exclusions Docker.",
    ),
    (
        "Admin Surface Discovery",
        re.compile(r"(/wp-admin|/phpmyadmin|/admin|/administrator|/manager)", re.I),
        58,
        70,
        "Confirmer qu aucun panneau d administration public n est expose.",
    ),
]

SEVERITY_BY_SCORE = ((85, "Critical"), (70, "High"), (45, "Medium"), (0, "Low"))


@dataclass
class Detection:
    title: str
    attack_type: str
    source_ip: str
    severity: str
    score: int
    confidence: int
    description: str
    evidence: list[str]
    recommendation: str


def severity_from_score(score: int) -> str:
    for threshold, severity in SEVERITY_BY_SCORE:
        if score >= threshold:
            return severity
    return "Low"


def parse_access_log(line: str) -> dict | None:
    match = LOG_RE.search(line.strip())
    if not match:
        return None
    item = match.groupdict()
    item["status"] = int(item["status"])
    item["decoded_path"] = unquote_plus(item["path"]).lower()
    return item


def _dedupe(detections: list[Detection]) -> list[Detection]:
    best: dict[tuple[str, str], Detection] = {}
    for detection in detections:
        key = (detection.source_ip, detection.attack_type)
        current = best.get(key)
        if current is None or detection.score > current.score:
            best[key] = detection
        else:
            current.evidence.extend(e for e in detection.evidence if e not in current.evidence)
            current.evidence = current.evidence[:8]
    return sorted(best.values(), key=lambda item: item.score, reverse=True)


def analyze_log_lines(lines: Iterable[str]) -> list[dict]:
    entries = [entry for line in lines if (entry := parse_access_log(line))]
    detections: list[Detection] = []
    by_ip: dict[str, list[dict]] = defaultdict(list)

    for entry in entries:
        by_ip[entry["ip"]].append(entry)
        payload = entry["decoded_path"]
        for attack_type, pattern, score, confidence, recommendation in PATTERNS:
            if not pattern.search(payload):
                continue
            detections.append(
                Detection(
                    title=f"{attack_type} detectee depuis {entry['ip']}",
                    attack_type=attack_type,
                    source_ip=entry["ip"],
                    severity=severity_from_score(score),
                    score=score,
                    confidence=confidence,
                    description=f"Requete suspecte {entry['method']} {entry['path']} retournee en HTTP {entry['status']}.",
                    evidence=[f"{entry['method']} {entry['path']} -> HTTP {entry['status']}"],
                    recommendation=recommendation,
                )
            )

    for ip, ip_entries in by_ip.items():
        auth_failures = [
            e for e in ip_entries
            if "/api/v1/auth/login" in e["decoded_path"] and e["status"] in {400, 401, 403, 429}
        ]
        not_found = [e for e in ip_entries if e["status"] == 404]
        sensitive_or_admin = [
            e for e in ip_entries
            if any(token in e["decoded_path"] for token in ("/.env", "/admin", "/wp-admin", "/phpmyadmin", "/config.php", "/backup"))
        ]

        if len(auth_failures) >= 5:
            score = min(95, 60 + len(auth_failures) * 5)
            detections.append(
                Detection(
                    title=f"Bruteforce authentification depuis {ip}",
                    attack_type="Credential Bruteforce",
                    source_ip=ip,
                    severity=severity_from_score(score),
                    score=score,
                    confidence=88,
                    description=f"{len(auth_failures)} echecs de connexion detectes sur la fenetre analysee.",
                    evidence=[f"{e['method']} {e['path']} -> HTTP {e['status']}" for e in auth_failures[:8]],
                    recommendation="Bloquer temporairement la source, imposer un delai progressif et verifier les comptes cibles.",
                )
            )

        if len(ip_entries) >= 25:
            score = min(88, 50 + len(ip_entries))
            detections.append(
                Detection(
                    title=f"Pic de trafic HTTP depuis {ip}",
                    attack_type="HTTP Flood / Reconnaissance",
                    source_ip=ip,
                    severity=severity_from_score(score),
                    score=score,
                    confidence=72,
                    description=f"{len(ip_entries)} requetes observees pour la meme source.",
                    evidence=[f"{e['method']} {e['path']} -> HTTP {e['status']}" for e in ip_entries[:8]],
                    recommendation="Appliquer un rate limiting, surveiller la charge et correler avec les logs applicatifs.",
                )
            )

        if len(not_found) >= 8 or len(sensitive_or_admin) >= 5:
            score = min(82, 55 + len(not_found) + len(sensitive_or_admin) * 2)
            detections.append(
                Detection(
                    title=f"Directory bruteforce depuis {ip}",
                    attack_type="Directory Bruteforce",
                    source_ip=ip,
                    severity=severity_from_score(score),
                    score=score,
                    confidence=84,
                    description="Enumeration de routes et fichiers sensibles detectee dans les logs Nginx.",
                    evidence=[f"{e['method']} {e['path']} -> HTTP {e['status']}" for e in (sensitive_or_admin or not_found)[:8]],
                    recommendation="Bloquer les chemins sensibles, activer le rate limiting et conserver les preuves.",
                )
            )

    return [asdict(detection) for detection in _dedupe(detections)[:20]]


def analyze_raw_logs(raw_logs: str) -> list[dict]:
    return analyze_log_lines(raw_logs.splitlines())
