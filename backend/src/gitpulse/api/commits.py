from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
import httpx

from gitpulse.config import Settings, get_settings
from gitpulse.github.client import fetch_commits, rate_limit_response_headers

router = APIRouter(tags=["commits"])


@router.get("/repos/{owner}/{repo}/commits")
async def list_commits(
    owner: str,
    repo: str,
    per_page: int = Query(30, ge=1, le=100),
    max_pages: int = Query(5, ge=1, le=50),
    settings: Settings = Depends(get_settings),
):
    """
    Proxy sample of GitHub commits with Link-header pagination and rate-limit headers.
    Set GITHUB_TOKEN in .env for higher rate limits (optional for public repos).
    """
    try:
        commits, gh_headers, pages_fetched = await fetch_commits(
            owner,
            repo,
            token=settings.github_token,
            per_page=per_page,
            max_pages=max_pages,
        )
    except httpx.HTTPStatusError as e:
        detail = e.response.text
        try:
            detail = e.response.json()
        except Exception:
            pass
        raise HTTPException(status_code=e.response.status_code, detail=detail) from e
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    extra_headers = rate_limit_response_headers(gh_headers)
    extra_headers["x-gitpulse-pages-fetched"] = str(pages_fetched)

    return JSONResponse(
        content={
            "owner": owner,
            "repo": repo,
            "count": len(commits),
            "pages_fetched": pages_fetched,
            "commits": commits,
        },
        headers=extra_headers,
    )
