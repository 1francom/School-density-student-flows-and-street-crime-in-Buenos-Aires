from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import requests

from utils import flatten_keyword_groups, unique_preserve_order


LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "google_cse"


class GoogleCustomSearchClient:
    endpoint = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, api_key: str | None = None, cse_id: str | None = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_CSE_API_KEY")
        self.cse_id = cse_id or os.getenv("GOOGLE_CSE_ID")

    @property
    def configured(self) -> bool:
        return bool(self.api_key and self.cse_id)

    def search(self, query: str, num: int = 5) -> list[SearchResult]:
        if not self.configured:
            raise RuntimeError("GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID are required for live search")

        params = {
            "key": self.api_key,
            "cx": self.cse_id,
            "q": query,
            "num": min(max(num, 1), 10),
        }
        response = requests.get(self.endpoint, params=params, timeout=20)
        response.raise_for_status()
        payload = response.json()
        items = payload.get("items", []) or []

        results: list[SearchResult] = []
        for item in items:
            title = item.get("title") or ""
            url = item.get("link") or ""
            snippet = item.get("snippet") or ""
            if title and url:
                results.append(SearchResult(title=title, url=url, snippet=snippet))
        return results


def build_queries(targets_config: dict[str, Any], keywords_config: dict[str, Any]) -> list[str]:
    role_terms = flatten_keyword_groups(keywords_config.get("role_keywords", {}))
    duration_terms = flatten_keyword_groups(keywords_config.get("duration_keywords", {}))
    country_terms: list[str] = []
    for country_data in (targets_config.get("countries", {}) or {}).values():
        country_terms.extend(country_data.get("search_terms", []) or [])

    organizations: list[str] = []
    for orgs in (targets_config.get("target_organizations", {}) or {}).values():
        organizations.extend(orgs or [])

    priority_role_terms = role_terms[:36]
    priority_duration_terms = duration_terms[:10]
    priority_country_terms = country_terms[:20]
    priority_organizations = organizations[:45]

    queries: list[str] = []
    for organization in priority_organizations:
        for role in priority_role_terms[:10]:
            queries.append(f'"{organization}" "{role}" jobs')

    for country in priority_country_terms:
        for role in priority_role_terms:
            queries.append(f'"{role}" "{country}" economics data risk internship trainee')

    for duration in priority_duration_terms:
        for role in priority_role_terms[:18]:
            queries.append(f'"{duration}" "{role}" economics analyst')

    return unique_preserve_order(queries)


def run_searches(
    client: GoogleCustomSearchClient,
    queries: list[str],
    max_queries: int = 60,
    results_per_query: int = 5,
) -> list[SearchResult]:
    all_results: list[SearchResult] = []
    selected_queries = queries[:max_queries]
    LOGGER.info("Running %s Google CSE queries", len(selected_queries))
    for index, query in enumerate(selected_queries, start=1):
        try:
            LOGGER.info("Search %s/%s: %s", index, len(selected_queries), query)
            all_results.extend(client.search(query, num=results_per_query))
        except requests.HTTPError as exc:
            LOGGER.warning("Search failed for query '%s': %s", query, exc)
        except requests.RequestException as exc:
            LOGGER.warning("Network error for query '%s': %s", query, exc)
        except Exception as exc:
            LOGGER.warning("Unexpected search error for query '%s': %s", query, exc)
    return all_results


def mock_search_results() -> list[SearchResult]:
    return [
        SearchResult(
            title="12-month Internship Economic Research and Data Analysis - ifo Institute",
            url="https://example.org/ifo-12-month-economic-research-internship",
            snippet=(
                "Munich, Germany. 12 months internship for final-year Bachelor students in economics. "
                "Tasks include R, Python, econometrics, causal inference and policy analysis."
            ),
            source="mock",
        ),
        SearchResult(
            title="Graduate Trainee Program Risk Analytics - Swiss Re",
            url="https://example.org/swiss-re-risk-analytics-trainee",
            snippet=(
                "Zurich, Switzerland. Trainee Program for Bachelor or Master graduates. Rotation in "
                "risk analytics, financial analytics, Python, Excel and data visualization. Duration unclear."
            ),
            source="mock",
        ),
        SearchResult(
            title="Senior Software Engineering Manager",
            url="https://example.org/senior-software-manager",
            snippet=(
                "Berlin, Germany. Permanent role requiring 5+ years experience. Lead frontend teams and "
                "manage software engineering delivery."
            ),
            source="mock",
        ),
        SearchResult(
            title="Pasantía análisis de datos economía - BBVA",
            url="https://example.org/bbva-pasantia-analisis-datos",
            snippet=(
                "Madrid, Spain. Pasantía de 6 a 12 meses para estudiante avanzado de economía. "
                "Python, Excel, BI dashboards, análisis de datos y riesgo financiero."
            ),
            source="mock",
        ),
    ]
