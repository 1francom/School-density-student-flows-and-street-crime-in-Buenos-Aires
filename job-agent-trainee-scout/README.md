# Job Agent Trainee Scout

Daily job scouting agent for Franco Medero, an LMU Munich Economics/VWL Bachelor student preparing for a Master's degree next year.

The agent searches, scores, summarizes and saves opportunities. It never applies to jobs and never sends recruiter messages.

## What It Prioritizes

- 12-month internships and Jahrespraktika
- 12-month trainee programs
- Graduate programs of 12 to 24 months when compatible with Master timing
- Research assistant, pre-doc and student research assistant roles
- Data analyst, risk analyst, BI, economic research and policy internships
- Junior analyst roles that accept Bachelor graduates or final-year Bachelor students

Target countries: Germany, Switzerland, Spain, Argentina and Sweden.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
GOOGLE_CSE_API_KEY=your_google_custom_search_api_key
GOOGLE_CSE_ID=your_google_custom_search_engine_id

# Optional email summary
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECIPIENT=recipient@example.com
```

For Gmail, use an app password rather than your normal account password.

## Daily Email Summary

After each successful daily run, the agent sends a plain-text summary to `mederofranco21@gmail.com` by default.

Gmail SMTP requires an App Password, not your normal Gmail password. Add these GitHub Secrets to enable email delivery:

- `EMAIL_SENDER`
- `EMAIL_PASSWORD`
- `EMAIL_RECIPIENT`

`EMAIL_RECIPIENT` can be omitted because it defaults to `mederofranco21@gmail.com`.

If `EMAIL_SENDER` or `EMAIL_PASSWORD` are missing, the workflow skips email sending, prints `Email skipped because EMAIL_SENDER or EMAIL_PASSWORD is missing.`, and still saves all results in the `jobs/` folder.

## Run Locally

Run with mocked search results:

```bash
python src/main.py --mock
```

Run with Google Custom Search:

```bash
python src/main.py
```

Optional controls:

```bash
python src/main.py --max-queries 80 --results-per-query 5
```

Outputs are saved to:

- `jobs/YYYY-MM-DD.csv`
- `jobs/YYYY-MM-DD.md`
- `jobs/YYYY-MM-DD.json`

Seen jobs are tracked in `data/seen_jobs.json` so repeated runs do not duplicate the same URLs.

## Configuration

- `config/targets.yaml`: countries, cities, and target organizations.
- `config/keywords.yaml`: multilingual role, duration, candidate-fit and exclusion terms.
- `config/scoring.yaml`: scoring weights and point values.

Final score is computed as:

```text
35% candidate_fit
30% duration_fit
20% role_fit
15% master_timing_fit
```

## GitHub Secrets

Add these repository secrets in GitHub:

- `GOOGLE_CSE_API_KEY`
- `GOOGLE_CSE_ID`
- `EMAIL_SENDER` optional
- `EMAIL_PASSWORD` optional
- `EMAIL_RECIPIENT` optional

Do not commit `.env` or any API keys.

## GitHub Actions

The workflow is at `.github/workflows/daily-job-search.yml`.

It:

1. Runs once per day via cron in the morning European time.
2. Can be started manually with `workflow_dispatch`.
3. Installs Python 3.11 dependencies.
4. Runs `python src/main.py`.
5. Commits new files in `jobs/` and updates `data/seen_jobs.json`.

To trigger it manually in GitHub:

1. Open the repository on GitHub.
2. Go to **Actions**.
3. Select **Daily Job Search**.
4. Click **Run workflow**.

## Notes

Google Custom Search snippets are not full job descriptions. Treat unclear duration, Master timing, pay and eligibility as manual-review flags before applying.
