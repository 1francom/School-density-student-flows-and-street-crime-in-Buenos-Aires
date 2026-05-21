from __future__ import annotations

import logging
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path}")
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected YAML mapping in {path}")
    return data


def today_iso() -> str:
    return date.today().isoformat()


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip().lower()


def contains_any(text: str, terms: list[str]) -> bool:
    text_norm = normalize_text(text)
    return any(_term_matches(text_norm, term) for term in terms)


def matching_terms(text: str, terms: list[str]) -> list[str]:
    text_norm = normalize_text(text)
    return [term for term in terms if _term_matches(text_norm, term)]


def _term_matches(text_norm: str, term: str) -> bool:
    term_norm = normalize_text(term)
    if not term_norm:
        return False
    if len(term_norm) <= 3 or re.fullmatch(r"[\w+#.]+", term_norm):
        return re.search(rf"(?<!\w){re.escape(term_norm)}(?!\w)", text_norm, flags=re.IGNORECASE) is not None
    return term_norm in text_norm


def flatten_keyword_groups(groups: dict[str, list[str]] | list[str]) -> list[str]:
    if isinstance(groups, list):
        return groups
    terms: list[str] = []
    for values in groups.values():
        terms.extend(values or [])
    return terms


def clamp_score(value: float) -> int:
    return max(0, min(100, round(value)))


def unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = normalize_text(value)
        if key and key not in seen:
            seen.add(key)
            result.append(value)
    return result
