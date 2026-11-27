"""Data e hora usadas nos registros."""

from __future__ import annotations

from datetime import datetime


def agora() -> str:
    """Data e hora atuais em ISO 8601, com fuso horário."""
    return datetime.now().astimezone().isoformat(timespec="seconds")
