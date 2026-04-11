"""Normalize stored media paths (DB keeps path-only URLs)."""

from urllib.parse import urlparse


def normalize_media_path(value: str) -> str:
    v = (value or "").strip()
    if not v:
        return v
    if v.startswith("http://") or v.startswith("https://"):
        parsed = urlparse(v)
        return (parsed.path or "").strip() or v
    return v
