from __future__ import annotations

from typing import Any

from utils import clamp_score, contains_any, matching_terms, normalize_text


def _text(job: dict[str, Any]) -> str:
    return " ".join(str(job.get(key, "")) for key in ("title", "snippet", "url", "detected_role_type"))


def score_duration(job: dict[str, Any], keywords_config: dict[str, Any]) -> int:
    text = _text(job)
    duration = normalize_text(job.get("detected_duration", ""))
    if "6 to 12" in duration:
        return 80
    if "12 months" in duration or "1 year" in duration:
        return 100
    if "too short" in duration or "too long" in duration:
        return 0
    if "trainee" in duration or "graduate" in duration:
        return 60
    role_signals = keywords_config.get("role_type_signals", {}) or {}
    relevant_terms = []
    for group in ("research", "data_bi", "risk_finance", "policy", "junior_analyst"):
        relevant_terms.extend(role_signals.get(group, []) or [])
    if contains_any(text, relevant_terms):
        return 40
    return 0


def score_master_timing(job: dict[str, Any], keywords_config: dict[str, Any]) -> int:
    text = _text(job)
    positives = (keywords_config.get("positive_signals", {}) or {}).get("master_compatible", []) or []
    negatives = keywords_config.get("negative_signals", {}) or {}
    duration = normalize_text(job.get("detected_duration", ""))

    if contains_any(text, negatives.get("phd_required", []) or []):
        return 0
    if contains_any(text, negatives.get("experience_5_plus", []) or []):
        return 0
    if "too long" in duration:
        return 0
    if "12 months" in duration or "1 year" in duration or contains_any(text, positives):
        return 100
    if "6 to 12" in duration or "trainee" in duration or "graduate" in duration:
        return 70
    if contains_any(text, negatives.get("master_required", []) or []):
        return 30
    return 70 if job.get("detected_role_type") != "manual review" else 30


def score_candidate_fit(job: dict[str, Any], keywords_config: dict[str, Any], scoring_config: dict[str, Any]) -> int:
    text = _text(job)
    candidate_signals = keywords_config.get("candidate_signals", {}) or {}
    positive_signals = keywords_config.get("positive_signals", {}) or {}
    negative_signals = keywords_config.get("negative_signals", {}) or {}
    points = scoring_config.get("positive_points", {}) or {}
    negative_points = scoring_config.get("negative_points", {}) or {}

    score = 20
    if contains_any(text, candidate_signals.get("economics", []) or []):
        score += points.get("economics_quantitative", 20)
    if contains_any(text, candidate_signals.get("econometrics", []) or []):
        score += points.get("economics_quantitative", 20)
    if contains_any(text, candidate_signals.get("data_tools", []) or []):
        score += points.get("tools", 15)
    if contains_any(text, candidate_signals.get("domains", []) or []):
        score += points.get("target_role_type", 25)
    if contains_any(text, candidate_signals.get("languages", []) or []):
        score += points.get("languages", 10)
    if contains_any(text, positive_signals.get("bachelor_fit", []) or []):
        score += points.get("bachelor_fit", 20)

    if contains_any(text, negative_signals.get("seniority", []) or []):
        score += negative_points.get("seniority", -40)
    if contains_any(text, negative_signals.get("phd_required", []) or []):
        score += negative_points.get("phd_required", -40)
    if contains_any(text, negative_signals.get("master_required", []) or []) and not contains_any(
        text, positive_signals.get("bachelor_fit", []) or []
    ):
        score += negative_points.get("master_required_without_bachelor", -30)
    if contains_any(text, negative_signals.get("experience_5_plus", []) or []):
        score += negative_points.get("experience_5_plus", -40)
    elif contains_any(text, negative_signals.get("experience_3_plus", []) or []):
        score += negative_points.get("experience_3_plus", -25)
    if contains_any(text, negative_signals.get("sales_only", []) or []):
        score += negative_points.get("sales_only", -25)
    if contains_any(text, negative_signals.get("pure_software", []) or []) and not contains_any(
        text, candidate_signals.get("domains", []) or []
    ):
        score += negative_points.get("pure_software", -20)

    return clamp_score(score)


def score_role_fit(job: dict[str, Any], keywords_config: dict[str, Any], scoring_config: dict[str, Any]) -> int:
    text = _text(job)
    role_signals = keywords_config.get("role_type_signals", {}) or {}
    duration_keywords = keywords_config.get("duration_keywords", {}) or {}
    positive_points = scoring_config.get("positive_points", {}) or {}
    negative_signals = keywords_config.get("negative_signals", {}) or {}
    negative_points = scoring_config.get("negative_points", {}) or {}

    score = 10
    if contains_any(text, duration_keywords.get("strong_12_month", []) or []):
        score += positive_points.get("strong_12_month", 30)
    if contains_any(text, role_signals.get("trainee", []) or []) or contains_any(
        text, role_signals.get("graduate_program", []) or []
    ):
        score += positive_points.get("trainee_or_graduate", 25)
    target_terms: list[str] = []
    for group in ("internship", "research", "data_bi", "risk_finance", "policy", "junior_analyst"):
        target_terms.extend(role_signals.get(group, []) or [])
    if contains_any(text, target_terms):
        score += positive_points.get("target_role_type", 25)

    if contains_any(text, negative_signals.get("seniority", []) or []):
        score += negative_points.get("seniority", -40)
    if contains_any(text, negative_signals.get("unpaid", []) or []):
        score += negative_points.get("unpaid", -20)
    if contains_any(text, negative_signals.get("sales_only", []) or []):
        score += negative_points.get("sales_only", -25)

    return clamp_score(score)


def recommended_cv_version(job: dict[str, Any], keywords_config: dict[str, Any]) -> str:
    text = _text(job)
    role_signals = keywords_config.get("role_type_signals", {}) or {}
    candidate_signals = keywords_config.get("candidate_signals", {}) or {}
    if contains_any(text, role_signals.get("research", []) or []) or contains_any(
        text, candidate_signals.get("econometrics", []) or []
    ):
        return "Research CV"
    if contains_any(text, role_signals.get("risk_finance", []) or []):
        return "Risk/Finance CV"
    if contains_any(text, ["climate", "ESG", "geospatial", "climate data"]):
        return "Climate/Geospatial CV"
    if contains_any(text, role_signals.get("data_bi", []) or []):
        return "Data/BI CV"
    return "General Trainee CV"


def build_reason(job: dict[str, Any], keywords_config: dict[str, Any]) -> str:
    text = _text(job)
    terms: list[str] = []
    for group in (keywords_config.get("candidate_signals", {}) or {}).values():
        terms.extend(matching_terms(text, group or []))
    for group in (keywords_config.get("role_type_signals", {}) or {}).values():
        terms.extend(matching_terms(text, group or []))
    terms.extend(matching_terms(text, (keywords_config.get("duration_keywords", {}) or {}).get("strong_12_month", []) or []))
    unique_terms = []
    for term in terms:
        if term not in unique_terms:
            unique_terms.append(term)
    if unique_terms:
        return "Matched signals: " + ", ".join(unique_terms[:8])
    return "Potentially relevant result, but limited details were available in the search snippet."


def build_concerns(job: dict[str, Any], keywords_config: dict[str, Any]) -> str:
    text = _text(job)
    concerns: list[str] = []
    negative_signals = keywords_config.get("negative_signals", {}) or {}
    for label, terms in negative_signals.items():
        if contains_any(text, terms or []):
            concerns.append(label.replace("_", " "))
    if job.get("detected_duration") == "unclear":
        concerns.append("duration unclear")
    if job.get("country") == "Unknown":
        concerns.append("country unclear")
    return "; ".join(concerns) if concerns else "None detected"


def score_job(job: dict[str, Any], keywords_config: dict[str, Any], scoring_config: dict[str, Any]) -> dict[str, Any]:
    candidate_fit = score_candidate_fit(job, keywords_config, scoring_config)
    duration_fit = score_duration(job, keywords_config)
    role_fit = score_role_fit(job, keywords_config, scoring_config)
    master_timing_fit = score_master_timing(job, keywords_config)
    weights = scoring_config.get("final_score_weights", {}) or {}
    final_score = clamp_score(
        candidate_fit * weights.get("candidate_fit", 0.35)
        + duration_fit * weights.get("duration_fit", 0.30)
        + role_fit * weights.get("role_fit", 0.20)
        + master_timing_fit * weights.get("master_timing_fit", 0.15)
    )

    return {
        **job,
        "candidate_fit": candidate_fit,
        "duration_fit": duration_fit,
        "role_fit": role_fit,
        "master_timing_fit": master_timing_fit,
        "final_score": final_score,
        "recommended_cv_version": recommended_cv_version(job, keywords_config),
        "reason_for_match": build_reason(job, keywords_config),
        "concerns": build_concerns(job, keywords_config),
    }
