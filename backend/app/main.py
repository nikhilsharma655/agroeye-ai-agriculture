"""
AgroEye FastAPI application entrypoint.
Run locally with: uvicorn app.main:app --reload
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import init_db
from app.utils.exceptions import (
    validation_exception_handler, http_exception_handler,
    sqlalchemy_exception_handler, unhandled_exception_handler,
)
from app.routes import (
    auth, users, farms, crops, recommendations, yield_routes,
    fertilizer, disease, irrigation, insights, analytics, webhooks, notifications,
)

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="AgroEye API",
    description="AI-powered smart agriculture platform — crop recommendation, yield prediction, "
                "fertilizer & irrigation guidance, disease-risk prediction, and farm analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(farms.router)
app.include_router(crops.router)
app.include_router(recommendations.router)
app.include_router(yield_routes.router)
app.include_router(fertilizer.router)
app.include_router(disease.router)
app.include_router(irrigation.router)
app.include_router(insights.router)
app.include_router(analytics.router)
app.include_router(webhooks.router)
app.include_router(notifications.router)


@app.on_event("startup")
def on_startup():
    # In production, schema is managed by Alembic migrations (see the
    # backend/alembic/ folder and the Docker entrypoint, which runs
    # `alembic upgrade head` before starting uvicorn). create_all() here is
    # kept only as a zero-config convenience for local development and the
    # test suite, and it only adds missing tables — it never alters existing
    # ones, so it's safe to leave enabled even when migrations are also used.
    init_db()


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"success": True, "message": "AgroEye API is running", "data": {"env": settings.APP_ENV}}


@app.get("/health", tags=["Health"], summary="Health check (for Docker/orchestration)")
def health():
    return {"success": True, "message": "OK", "data": None}
