from fastapi import FastAPI, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from typing import Optional

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.analyze import router as analyze_router
from app.api.routes.uploads import router as uploads_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.analyze_job import router as analyze_job_router
from app.schemas.entities import AnalysisResponse
from app.services.hf import get_hf_service
from app.db.session import init_engine_and_create_all


def create_app() -> FastAPI:
    app = FastAPI(
        title="MediViewAI",
        default_response_class=ORJSONResponse,
        version="0.1.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(analyze_router)
    app.include_router(uploads_router)
    app.include_router(jobs_router)
    app.include_router(analyze_job_router)

    @app.on_event("startup")
    def _on_startup() -> None:
        init_engine_and_create_all()

    # routes are registered via routers

    return app


app = create_app()

