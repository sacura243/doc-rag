from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import load_api_settings
from api.routers.auth import router as auth_router
from api.routers.health import router as health_router


def create_app() -> FastAPI:
    settings = load_api_settings()
    app = FastAPI(title="Enterprise Knowledge Base API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
    )
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")

    return app
