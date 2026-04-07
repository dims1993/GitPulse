from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "online",
    "message": "GitPulse backend is running"
    }