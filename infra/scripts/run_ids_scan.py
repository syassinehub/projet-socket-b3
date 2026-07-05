#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from urllib import error, request


ROOT = Path(__file__).resolve().parents[2]
LOG_FILE = ROOT / "infra" / "nginx" / "logs" / "access.log"
OFFSET_FILE = ROOT / "infra" / "nginx" / "logs" / ".ids_offset"
API_URL = os.getenv("SOCKET_API_URL", "http://localhost/api/v1/ingest/nginx-logs")


def load_env() -> dict[str, str]:
    env_path = ROOT / ".env"
    values: dict[str, str] = {}
    if not env_path.exists():
        return values
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"')
    return values


def read_logs() -> str:
    if LOG_FILE.exists() and LOG_FILE.stat().st_size > 0:
        size = LOG_FILE.stat().st_size
        try:
            offset = int(OFFSET_FILE.read_text(encoding="utf-8"))
        except (FileNotFoundError, ValueError):
            offset = 0
        if offset > size:
            offset = 0
        with LOG_FILE.open("r", encoding="utf-8", errors="ignore") as handle:
            handle.seek(offset)
            raw = handle.read()
            OFFSET_FILE.write_text(str(handle.tell()), encoding="utf-8")
        return raw
    result = subprocess.run(["docker", "logs", "--since", "10m", "socket-nginx"], capture_output=True, text=True, check=False)
    return result.stdout + result.stderr


def post_logs(raw_logs: str, token: str) -> dict:
    payload = json.dumps({"raw_logs": raw_logs}).encode()
    req = request.Request(API_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("X-SOCket-Sensor-Token", token)
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode())


def main() -> int:
    token = os.getenv("SENSOR_TOKEN") or load_env().get("SENSOR_TOKEN")
    if not token:
        print("SENSOR_TOKEN introuvable", file=sys.stderr)
        return 2
    raw_logs = read_logs()
    if not raw_logs.strip():
        print("Aucun log Nginx a analyser")
        return 0
    try:
        result = post_logs(raw_logs, token)
    except error.HTTPError as exc:
        print(exc.read().decode(), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
