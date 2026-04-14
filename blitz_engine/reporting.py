"""Serialization helpers for Blitz Engine outputs."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any


def to_serializable(value: Any) -> Any:
    """Recursively convert dataclasses and tuples into JSON-safe values."""
    if is_dataclass(value):
        value = asdict(value)

    if isinstance(value, dict):
        return {key: to_serializable(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_serializable(item) for item in value]

    return value


def dumps_report(value: Any, indent: int = 2) -> str:
    """Serialize an output object into formatted JSON."""
    return json.dumps(to_serializable(value), indent=indent, sort_keys=True)
