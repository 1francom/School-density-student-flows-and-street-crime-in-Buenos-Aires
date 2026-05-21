from __future__ import annotations

import re
from typing import Any

from utils import contains_any, matching_terms, normalize_text


def combined_text(result: dict[str, Any]) -> str:
    return " ".join(
        str(result.get(key, ""))
        for key in ("title", "snippet", "url")
        if result.get(key)
    )


def detect_role_type(text: str, keywords_config: dict[str, Any]) -> str:
    role_signals = keywords_config.get("role_type_signals", {}) or {}
    detected_duration = detect_duration(text, keywords_config)
    if contains_any(text, role_signals.get("internship", []) or []):
        if detected_duration == "12 months / 1 year":
            return "12-month internship"
        return "internship"
    priority = [
        ("trainee program", ["trainee"]),
        ("graduate program", ["graduate_program"]),
        ("research assistant / pre-doc", ["research"]),
        ("data / BI analyst", ["data_bi"]),
        ("risk / finance analyst", ["risk_finance"]),
        ("policy analyst", ["policy"]),
        ("junior analyst", ["junior_analyst"]),
    ]
    for label, groups in priority:
        terms: list[str] = []
        for group in groups:
            terms.extend(role_signals.get(group, []) or [])
        if contains_any(text, terms):
            return label
    return "manual review"


def detect_duration(text: str, keywords_config: dict[str, Any]) -> str:
    duration_keywords = keywords_config.get("duration_keywords", {}) or {}
    if contains_any(text, duration_keywords.get("strong_12_month", []) or []):
        return "12 months / 1 year"
    if contains_any(text, duration_keywords.get("six_to_twelve", []) or []):
        return "6 to 12 months"
    if contains_any(text, duration_keywords.get("too_short", []) or []):
        return "too short"
    if contains_any(text, duration_keywords.get("too_long", []) or []):
        return "too long or permanent"
    if contains_any(text, (keywords_config.get("role_type_signals", {}) or {}).get("trainee", []) or []):
        return "trainee duration unclear"
    if contains_any(text, (keywords_config.get("role_type_signals", {}) or {}).get("graduate_program", []) or []):
        return "graduate program duration unclear"
    return "unclear"


def detect_country(text: str, targets_config: dict[str, Any]) -> str:
    for country, country_data in (targets_config.get("countries", {}) or {}).items():
        terms = [country] + (country_data.get("search_terms", []) or [])
        if contains_any(text, terms):
            return country
    return "Unknown"


def detect_city_or_remote(text: str) -> str:
    text_norm = normalize_text(text)
    if "remote" in text_norm or "hybrid" in text_norm or "home office" in text_norm:
        return "Remote / hybrid possible"

    cities = [
        "Munich",
        "München",
        "Frankfurt",
        "Berlin",
        "Zurich",
        "Zürich",
        "Geneva",
        "Madrid",
        "Barcelona",
        "Buenos Aires",
        "Stockholm",
    ]
    matches = matching_terms(text, cities)
    return matches[0] if matches else "Unknown"


def infer_company_or_institution(title: str, url: str) -> str:
    separators = [" - ", " | ", " at ", " bei ", " en "]
    for separator in separators:
        if separator in title:
            candidate = title.split(separator)[-1].strip()
            if 2 <= len(candidate) <= 80:
                return candidate

    domain_match = re.search(r"https?://(?:www\.)?([^/]+)", url)
    if domain_match:
        return domain_match.group(1)
    return "Unknown"


def classify_result(
    raw_result: dict[str, Any],
    targets_config: dict[str, Any],
    keywords_config: dict[str, Any],
) -> dict[str, Any]:
    text = combined_text(raw_result)
    title = raw_result.get("title", "")
    url = raw_result.get("url", "")
    return {
        **raw_result,
        "company_or_institution": infer_company_or_institution(title, url),
        "country": detect_country(text, targets_config),
        "city_or_remote": detect_city_or_remote(text),
        "detected_role_type": detect_role_type(text, keywords_config),
        "detected_duration": detect_duration(text, keywords_config),
    }
