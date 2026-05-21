from __future__ import annotations

import logging
import os
import smtplib
from datetime import date
from email.mime.text import MIMEText
from typing import Any


LOGGER = logging.getLogger(__name__)
DEFAULT_EMAIL_RECIPIENT = "mederofranco21@gmail.com"
EMAIL_SUBJECT = "Daily Job Scout — Trainee & Internship Opportunities"


def email_config_available() -> bool:
    return bool(os.getenv("EMAIL_SENDER") and os.getenv("EMAIL_PASSWORD"))


def _search_date(results: list[dict[str, Any]]) -> str:
    if results:
        first_date = results[0].get("date_found")
        if first_date:
            return str(first_date)
    return date.today().isoformat()


def _sort_results(results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(results, key=lambda item: item.get("final_score", 0), reverse=True)


def _opportunity_block(job: dict[str, Any], index: int) -> str:
    return "\n".join(
        [
            f"{index}. {job.get('title', 'Untitled opportunity')}",
            f"   Company/institution: {job.get('company_or_institution', 'Unknown')}",
            f"   Location: {job.get('country', 'Unknown')} / {job.get('city_or_remote', 'Unknown')}",
            f"   Final score: {job.get('final_score', '')}",
            f"   Role type: {job.get('detected_role_type', 'Unknown')}",
            f"   Duration: {job.get('detected_duration', 'Unknown')}",
            f"   Recommended CV: {job.get('recommended_cv_version', 'General Trainee CV')}",
            f"   Reason: {job.get('reason_for_match', '')}",
            f"   Concerns: {job.get('concerns', 'None detected')}",
            f"   URL: {job.get('url', '')}",
        ]
    )


def _render_section(title: str, results: list[dict[str, Any]], empty_message: str) -> str:
    lines = [title, "-" * len(title)]
    if not results:
        lines.append(empty_message)
        return "\n".join(lines)
    for index, job in enumerate(results, start=1):
        lines.append(_opportunity_block(job, index))
        lines.append("")
    return "\n".join(lines).rstrip()


def _build_email_body(results: list[dict[str, Any]], summary_path: str | None = None) -> str:
    sorted_results = _sort_results(results)
    search_date = _search_date(sorted_results)
    best_12_month = [job for job in sorted_results if job.get("duration_fit", 0) >= 100]
    manual_review = [
        job
        for job in sorted_results
        if job.get("final_score", 0) < 65
        or "unclear" in str(job.get("concerns", "")).lower()
        or "manual review" in str(job.get("detected_role_type", "")).lower()
    ]

    lines = [
        "Daily Job Scout summary",
        "",
        f"Date of search: {search_date}",
        f"New opportunities found: {len(results)}",
        "",
    ]

    if not sorted_results:
        lines.extend(
            [
                "No new suitable opportunities were found today.",
                "",
                "Saved job result files were still updated normally.",
            ]
        )
    else:
        lines.append(
            _render_section(
                "Top 10 opportunities ranked by final_score",
                sorted_results[:10],
                "No opportunities available.",
            )
        )
        if best_12_month:
            lines.extend(
                [
                    "",
                    _render_section(
                        "Best 12-month opportunities",
                        best_12_month,
                        "No 12-month opportunities available.",
                    ),
                ]
            )
        if manual_review:
            lines.extend(
                [
                    "",
                    _render_section(
                        "Roles needing manual review",
                        manual_review,
                        "No roles need manual review.",
                    ),
                ]
            )

    if summary_path:
        lines.extend(["", f"Markdown summary saved at: {summary_path}"])

    lines.extend(
        [
            "",
            "This email was sent only to the configured user recipient. No recruiters or companies were contacted.",
        ]
    )
    return "\n".join(lines)


def send_email_summary(results: list[dict], summary_path: str | None = None) -> None:
    if not email_config_available():
        LOGGER.warning("Email skipped because EMAIL_SENDER or EMAIL_PASSWORD is missing.")
        return

    sender = os.environ["EMAIL_SENDER"]
    password = os.environ["EMAIL_PASSWORD"]
    recipient = os.getenv("EMAIL_RECIPIENT") or DEFAULT_EMAIL_RECIPIENT

    body = _build_email_body(results, summary_path)
    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = EMAIL_SUBJECT
    message["From"] = sender
    message["To"] = recipient

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, [recipient], message.as_string())
        LOGGER.info("Email summary sent to %s", recipient)
    except Exception as exc:
        LOGGER.warning("Email delivery failed; saved job results were not affected. Error: %s", exc)
