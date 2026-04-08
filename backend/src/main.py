from fastapi import FastAPI
from gitpulse.api.commits import router as commits_router

app = FastAPI()
app.include_router(commits_router, prefix="/api")


@app.get("/")
def read_root():
    return {
        "service": "GitPulse API",
        "message": "Open /docs to try endpoints, or fetch commits below.",
        "docs": "/docs",
        "health": "/health",
        "commits_example": "/api/repos/facebook/react/commits",
        "commits_pattern": "/api/repos/{owner}/{repo}/commits",
    }

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "online",
    "message": "GitPulse backend is running"
    }
