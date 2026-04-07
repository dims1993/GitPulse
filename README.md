# GitPulse

**I built GitPulse to help engineering managers understand team culture through Git data—surfacing fatigue signals and weak commit hygiene before they become a larger problem.**

GitPulse goes beyond naive “positive vs negative” labels. It extracts **actionable metrics** from a GitHub repository: how people write commits, when work happens, language consistency, and a simple **quality score** you can track over time.

## Core capabilities (roadmap)

| Area | What we measure |
|------|------------------|
| **Commit sentiment & tone** | NLP on commit messages—clear/professional vs frustrated or vague (“fix please god”, “i hate this”). |
| **Burnout signals** | Patterns such as unusually high commit volume at very late hours (e.g. 3:00 AM local)—alerts, not diagnoses. |
| **Language consistency** | e.g. expected professional language (often English)—how often the team drifts. |
| **Quality dashboard** | Score (1–10) from message clarity and integration frequency (merges/PR cadence). |

## Stack

- **Backend:** Python (NLP with [TextBlob](https://textblob.readthedocs.io/); API layer TBD).
- **Frontend:** TypeScript + React (charts and dashboard).
- **Data:** **PostgreSQL** for durable storage and analytics-friendly queries. (Redis-style caching can be added later if GitHub rate limits require it.)
- **GitHub:** REST API first; **OAuth “Sign in with GitHub”** and **webhooks** for near–real-time updates are planned.
- **Exports:** Monthly executive PDF report (planned).

## Repository layout

```
backend/    # Python API and analysis jobs
frontend/   # React + TypeScript dashboard
```

## How we are building this

We are implementing GitPulse **incrementally**: small commits, each with a clear story, so the project stays easy to explain in interviews.

**Suggested phases**

1. **Bootstrap** — layout, tooling, README (you are here).
2. **Backend skeleton** — FastAPI app, config, health check.
3. **GitHub read path** — fetch commits for a repo (authenticated requests, pagination).
4. **Analysis** — TextBlob sentiment + simple rules; persist snapshots in PostgreSQL.
5. **Frontend** — auth flow, repo picker, first charts.
6. **OAuth + webhooks** — no pasted tokens; live updates on push.
7. **PDF export** — monthly report download.

## License

MIT (unless you prefer otherwise—update this file when you decide).
