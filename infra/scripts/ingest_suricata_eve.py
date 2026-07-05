#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys
from urllib import error, request


ROOT = Path(__file__).resolve().parents[2]
LIVE_EVE_FILE = ROOT / "infra" / "suricata" / "logs" / "eve.json"
SAMPLE_EVE_FILE = ROOT / "infra" / "suricata" / "sample_eve.json"
OFFSET_FILE = ROOT / "infra" / "suricata" / "logs" / ".eve_offset"
API_URL = os.getenv("SOCKET_API_URL", "http://localhost/api/v1/ingest/suricata-eve")


def load_env() -> dict[str, str]:
    values: dict[str, str] = {}
    env_path = ROOT / ".env"
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def read_with_offset(path: Path) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    size = path.stat().st_size
    try:
        offset = int(OFFSET_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        offset = 0
    if offset > size:
        offset = 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        handle.seek(offset)
        raw = handle.read()
        OFFSET_FILE.write_text(str(handle.tell()), encoding="utf-8")
    return raw


def select_source(args: argparse.Namespace) -> tuple[Path, bool, str]:
    if args.file:
        return Path(args.file), False, "fichier fourni"
    if args.sample:
        return SAMPLE_EVE_FILE, False, "fichier EVE de demonstration"
    if LIVE_EVE_FILE.exists() and LIVE_EVE_FILE.stat().st_size > 0:
        return LIVE_EVE_FILE, not args.no_offset, "eve.json Suricata live"
    return SAMPLE_EVE_FILE, False, "fichier EVE de demonstration"


def post_events(raw_events: str, token: str) -> dict:
    payload = json.dumps({"raw_events": raw_events}).encode()
    req = request.Request(API_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-SOCket-Sensor-Token", token)
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingere des alertes Suricata EVE JSON dans SOCket.")
    parser.add_argument("--sample", action="store_true", help="Utilise le fichier sample_eve.json.")
    parser.add_argument("--file", help="Chemin vers un fichier EVE JSON specifique.")
    parser.add_argument("--no-offset", action="store_true", help="Relit tout eve.json au lieu de seulement les nouveaux evenements.")
    args = parser.parse_args()

    token = os.getenv("SENSOR_TOKEN") or load_env().get("SENSOR_TOKEN")
    if not token:
        print("SENSOR_TOKEN introuvable", file=sys.stderr)
        return 2

    source, use_offset, source_label = select_source(args)
    if not source.exists():
        print(f"Fichier EVE introuvable: {source}", file=sys.stderr)
        return 2

    raw_events = read_with_offset(source) if use_offset else source.read_text(encoding="utf-8")
    if not raw_events.strip():
        print(f"Aucun nouvel evenement Suricata dans {source}")
        return 0

    try:
        result = post_events(raw_events, token)
    except error.HTTPError as exc:
        print(exc.read().decode(), file=sys.stderr)
        return 1

    print(f"Source: {source_label} ({source})")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
