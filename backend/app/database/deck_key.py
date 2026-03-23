"""Canonical deck grouping key: unique anime_name in DB matches this value."""


def canonical_deck_key(anime_name: str | None, anime_link: str | None) -> str | None:
    """
    Same logic as migration SQL:
    COALESCE(NULLIF(TRIM(COALESCE(anime_name, '')), ''), NULLIF(TRIM(COALESCE(anime_link, '')), ''))
    """
    name_part = (anime_name or "").strip()
    name_part = name_part if name_part else None
    link_part = (anime_link or "").strip()
    link_part = link_part if link_part else None
    return name_part or link_part
