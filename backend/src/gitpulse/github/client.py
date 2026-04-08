from __future__ import annotations

import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)

GITHUB_API = "https://api.github.com"


def _parse_next_url(link_header: str | None) -> str | None:
    """Return the URL for rel=\"next\" from a GitHub Link header, if present."""
    if not link_header:
        return None
    for part in link_header.split(","):
        section = part.strip()
        if 'rel="next"' not in section and "rel='next'" not in section:
            continue
        start = section.find("<") + 1
        end = section.find(">")
        if start > 0 and end > start:
            return section[start:end]
    return None


def _rate_limit_log_fields(headers: httpx.Headers) -> dict[str, str]:
    out: dict[str, str] = {}
    for key in (
        "x-ratelimit-limit",
        "x-ratelimit-remaining",
        "x-ratelimit-reset",
        "x-ratelimit-used",
    ):
        if key in headers:
            out[key] = headers[key]
    return out


def rate_limit_response_headers(headers: httpx.Headers) -> dict[str, str]:
    """Forward GitHub rate-limit headers to our JSONResponse (debug-friendly)."""
    pairs = (
        ("x-ratelimit-limit", "x-github-ratelimit-limit"),
        ("x-ratelimit-remaining", "x-github-ratelimit-remaining"),
        ("x-ratelimit-reset", "x-github-ratelimit-reset"),
        ("x-ratelimit-used", "x-github-ratelimit-used"),
    )
    return {out: headers[src] for src, out in pairs if src in headers}


async def fetch_commits(
    owner: str,
    repo: str,
    *,
    token: str | None,
    per_page: int = 30,
    max_pages: int = 5,
    client: httpx.AsyncClient | None = None,
) -> tuple[list[dict[str, Any]], httpx.Headers, int]:
    """
    Fetch commits from GitHub, following Link rel=\"next\" until exhausted or max_pages.

    Returns (commits_json, last_response_headers, pages_fetched).
    """
    per_page = max(1, min(per_page, 100))
    max_pages = max(1, min(max_pages, 50))

    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    params: dict[str, Any] = {"per_page": per_page}

    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    own_client = client is None
    http = client or httpx.AsyncClient(timeout=30.0)

    all_commits: list[dict[str, Any]] = []
    pages = 0
    last_headers: httpx.Headers = httpx.Headers()

    try:
        next_url: str | None = url
        next_params: dict[str, Any] | None = params

        while next_url and pages < max_pages:
            if next_params is not None:
                response = await http.get(next_url, params=next_params, headers=headers)
            else:
                response = await http.get(next_url, headers=headers)

            last_headers = response.headers
            rl = _rate_limit_log_fields(response.headers)
            if rl:
                logger.info("GitHub rate limit: %s", rl)

            response.raise_for_status()
            batch = response.json()
            if not isinstance(batch, list):
                break
            all_commits.extend(batch)
            pages += 1

            link = response.headers.get("link")
            next_url = _parse_next_url(link)
            next_params = None
    finally:
        if own_client:
            await http.aclose()

    return all_commits, last_headers, pages
