from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from utils import normalize_text


RESULT_COLUMNS = [
    "date_found",
    "title",
    "company_or_institution",
    "country",
    "city_or_remote",
    "url",
    "snippet",
    "detected_role_type",
    "detected_duration",
    "candidate_fit",
    "duration_fit",
    "role_fit",
    "master_timing_fit",
    "final_score",
    "recommended_cv_version",
    "reason_for_match",
    "concerns",
]


def job_key(job: dict[str, Any]) -> str:
    stable = normalize_text(job.get("url")) or normalize_text(job.get("title"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]


def load_seen(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
            return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def save_seen(path: Path, seen: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(seen, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.write("\n")


def dedupe_new_jobs(jobs: list[dict[str, Any]], seen: dict[str, Any]) -> list[dict[str, Any]]:
    new_jobs: list[dict[str, Any]] = []
    local_seen: set[str] = set()
    for job in jobs:
        key = job_key(job)
        if key in seen or key in local_seen:
            continue
        local_seen.add(key)
        new_jobs.append({**job, "_job_key": key})
    return new_jobs


def update_seen(seen: dict[str, Any], jobs: list[dict[str, Any]]) -> dict[str, Any]:
    for job in jobs:
        key = job.get("_job_key") or job_key(job)
        seen[key] = {
            "title": job.get("title"),
            "url": job.get("url"),
            "date_found": job.get("date_found"),
            "final_score": job.get("final_score"),
        }
    return seen


def _frame(jobs: list[dict[str, Any]]) -> pd.DataFrame:
    rows = [{column: job.get(column, "") for column in RESULT_COLUMNS} for job in jobs]
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)


def save_outputs(jobs: list[dict[str, Any]], jobs_dir: Path, date_string: str) -> dict[str, Path]:
    jobs_dir.mkdir(parents=True, exist_ok=True)
    csv_path = jobs_dir / f"{date_string}.csv"
    json_path = jobs_dir / f"{date_string}.json"
    md_path = jobs_dir / f"{date_string}.md"

    sorted_jobs = sorted(jobs, key=lambda item: item.get("final_score", 0), reverse=True)
    df = _frame(sorted_jobs)
    df.to_csv(csv_path, index=False, encoding="utf-8")
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(df.to_dict(orient="records"), handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    md_path.write_text(render_markdown_summary(sorted_jobs, date_string), encoding="utf-8")
    return {"csv": csv_path, "json": json_path, "markdown": md_path}


def _markdown_table(jobs: list[dict[str, Any]], limit: int = 10) -> str:
    if not jobs:
        return "_No matching opportunities in this section._\n"
    lines = [
        "| Score | Title | Company | Country | Duration | CV | Concerns |",
        "|---:|---|---|---|---|---|---|",
    ]
    for job in jobs[:limit]:
        title = str(job.get("title", "")).replace("|", "\\|")
        url = job.get("url", "")
        company = str(job.get("company_or_institution", "")).replace("|", "\\|")
        lines.append(
            f"| {job.get('final_score', '')} | [{title}]({url}) | {company} | "
            f"{job.get('country', '')} | {job.get('detected_duration', '')} | "
            f"{job.get('recommended_cv_version', '')} | {job.get('concerns', '')} |"
        )
    return "\n".join(lines) + "\n"


def _section_matches(job: dict[str, Any], terms: list[str]) -> bool:
    text = " ".join(
        str(job.get(key, ""))
        for key in ("title", "snippet", "detected_role_type", "recommended_cv_version")
    ).lower()
    return any(term.lower() in text for term in terms)


def render_markdown_summary(jobs: list[dict[str, Any]], date_string: str) -> str:
    top = sorted(jobs, key=lambda item: item.get("final_score", 0), reverse=True)
    best_12 = [job for job in top if job.get("duration_fit", 0) >= 100]
    research = [job for job in top if _section_matches(job, ["research", "pre-doc", "predoc", "institute", "econometrics"])]
    data_bi = [job for job in top if _section_matches(job, ["data", "business intelligence", "bi analyst", "dashboard"])]
    risk_finance = [job for job in top if _section_matches(job, ["risk", "finance", "financial", "bank", "insurance"])]
    manual_review = [
        job
        for job in top
        if job.get("final_score", 0) < 65
        or "unclear" in normalize_text(job.get("concerns"))
        or "manual review" in normalize_text(job.get("detected_role_type"))
    ]

    sections = [
        f"# Daily Job Scout - {date_string}",
        "",
        "## Top 10 opportunities today",
        _markdown_table(top, 10),
        "## Best 12-month opportunities",
        _markdown_table(best_12, 10),
        "## Best research/institute opportunities",
        _markdown_table(research, 10),
        "## Best data/BI opportunities",
        _markdown_table(data_bi, 10),
        "## Best risk/finance opportunities",
        _markdown_table(risk_finance, 10),
        "## Roles needing manual review",
        _markdown_table(manual_review, 15),
    ]
    return "\n".join(sections)
