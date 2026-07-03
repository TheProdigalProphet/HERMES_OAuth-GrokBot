from fastapi import FastAPI
from src.api.profile import router as profile_router
from src.api.jobs import router as jobs_router
from src.api.network import router as network_router
from src.api.health import router as health_router
from src.api.manifest import router as manifest_router
from src.api.background import router as background_router
from src.api.auth import router as auth_router
from src.api.evidence import router as evidence_router
from src.api.chat import router as chat_router

app = FastAPI(title="Hermes AI LinkedIn Agent")
app.include_router(profile_router, prefix="/profile", tags=["profile"])
app.include_router(jobs_router, prefix="/jobs", tags=["jobs"])
app.include_router(network_router, prefix="/network", tags=["network"])
app.include_router(health_router, prefix="", tags=["health"])
app.include_router(manifest_router, prefix="", tags=["manifest"])
app.include_router(background_router, prefix="", tags=["background"])
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(evidence_router, prefix="", tags=["evidence"])
app.include_router(chat_router, prefix="", tags=["chat"])

@app.get("/")
def root():
    return {"message": "Welcome to Hermes Agent LinkedIn Assistant"}
