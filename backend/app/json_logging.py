"""Structured JSON lines on stdout for Loki / Grafana (| json)."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone

_configured: str | None = None  # "json" | "plain"


class StructuredJsonFormatter(logging.Formatter):
    """One line = one JSON object; merges record.http_audit when present."""

    def format(self, record: logging.LogRecord) -> str:
        ts = datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat()
        line: dict[str, object] = {
            "ts": ts,
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        audit = getattr(record, "http_audit", None)
        if audit is not None:
            line.update(audit)
        if record.exc_info:
            line["exception"] = self.formatException(record.exc_info).rstrip()
        return json.dumps(line, ensure_ascii=False)


def configure_json_app_logging(enabled: bool) -> None:
    """Call once per process (web, scheduler, CLI). Idempotent."""
    global _configured
    if _configured is not None:
        return

    root = logging.getLogger()

    if not enabled:
        if not root.handlers:
            logging.basicConfig(level=logging.INFO)
        _configured = "plain"
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())

    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "uvicorn.asgi"):
        log = logging.getLogger(name)
        log.handlers.clear()
        log.propagate = True

    http_audit = logging.getLogger("http.audit")
    http_audit.handlers.clear()
    http_audit.propagate = True
    http_audit.setLevel(logging.INFO)

    _configured = "json"
