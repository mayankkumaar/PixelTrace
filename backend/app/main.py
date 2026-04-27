from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_router
from app.core.config import settings
from app.db.session import Base, engine
from app import models  # noqa: F401

settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.samples_dir.mkdir(parents=True, exist_ok=True)
settings.frontend_dir.mkdir(parents=True, exist_ok=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Forensic Watermarking API",
    version="1.0.0",
    description="ML-assisted pixel watermarking and forensic attribution backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.mount("/frontend", StaticFiles(directory=str(settings.frontend_dir)), name="frontend")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


@app.get("/")
def serve_frontend():
    index_path = settings.frontend_dir / "index.html"
    if not index_path.exists():
        return {"message": "Frontend not found. Create frontend/index.html"}
    return FileResponse(path=str(index_path), media_type="text/html")
