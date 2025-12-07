# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api import analyze, complete, health, admin, compliance
from .policy.rag_store import init_policy_rag
from .ml.safety_classifier import init_safety_classifier


def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME)

    # CORS for frontend
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "*",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup_event():
        # Load policy RAG index + safety classifier at startup
        init_policy_rag()
        init_safety_classifier()

    # Routers
    app.include_router(health.router, prefix=settings.API_V1_PREFIX)
    app.include_router(analyze.router, prefix=settings.API_V1_PREFIX)
    app.include_router(complete.router, prefix=settings.API_V1_PREFIX)
    app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
    app.include_router(compliance.router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
