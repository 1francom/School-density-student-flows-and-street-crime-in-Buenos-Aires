from __future__ import annotations

import argparse
import logging
import os
from dataclasses import asdict

from dotenv import load_dotenv

from classify import classify_result
from notify import send_email_summary
from score import score_job
from search import GoogleCustomSearchClient, build_queries, mock_search_results, run_searches
from storage import dedupe_new_jobs, load_seen, save_outputs, save_seen, update_seen
from utils import ROOT_DIR, load_yaml, setup_logging, today_iso


LOGGER = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Daily job scouting agent for trainee and internship roles.")
    parser.add_argument("--mock", action="store_true", help="Use built-in mocked search results instead of Google CSE.")
    parser.add_argument("--date", help="Override output date, useful for testing.")
    parser.add_argument("--max-queries", type=int, default=int(os.getenv("JOB_AGENT_MAX_QUERIES", "60")))
    parser.add_argument("--results-per-query", type=int, default=int(os.getenv("JOB_AGENT_RESULTS_PER_QUERY", "5")))
    return parser.parse_args()


def main() -> int:
    setup_logging()
    load_dotenv(ROOT_DIR / ".env")
    args = parse_args()
    date_string = args.date or today_iso()

    targets_config = load_yaml(ROOT_DIR / "config" / "targets.yaml")
    keywords_config = load_yaml(ROOT_DIR / "config" / "keywords.yaml")
    scoring_config = load_yaml(ROOT_DIR / "config" / "scoring.yaml")

    use_mock = args.mock or os.getenv("JOB_AGENT_USE_MOCK", "").lower() in {"1", "true", "yes"}
    if use_mock:
        LOGGER.info("Using mocked search results")
        raw_results = [asdict(result) for result in mock_search_results()]
    else:
        client = GoogleCustomSearchClient()
        if not client.configured:
            LOGGER.error("Missing GOOGLE_CSE_API_KEY or GOOGLE_CSE_ID. Use --mock for local testing.")
            return 2
        queries = build_queries(targets_config, keywords_config)
        raw_results = [asdict(result) for result in run_searches(client, queries, args.max_queries, args.results_per_query)]

    LOGGER.info("Raw results collected: %s", len(raw_results))
    classified = [classify_result(result, targets_config, keywords_config) for result in raw_results]
    scored = [score_job(job, keywords_config, scoring_config) for job in classified]

    for job in scored:
        job["date_found"] = date_string

    seen_path = ROOT_DIR / "data" / "seen_jobs.json"
    seen = load_seen(seen_path)
    new_jobs = dedupe_new_jobs(scored, seen)
    LOGGER.info("New opportunities after deduplication: %s", len(new_jobs))

    output_paths = save_outputs(new_jobs, ROOT_DIR / "jobs", date_string)
    seen = update_seen(seen, new_jobs)
    save_seen(seen_path, seen)

    LOGGER.info("Saved CSV: %s", output_paths["csv"])
    LOGGER.info("Saved JSON: %s", output_paths["json"])
    LOGGER.info("Saved Markdown: %s", output_paths["markdown"])
    send_email_summary(new_jobs, summary_path=str(output_paths["markdown"]))
    LOGGER.info("Run complete. No applications or recruiter messages were sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
