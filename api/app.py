"""
FastAPI Application Setup

Provides an entry point for running the API backend.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from core.air_gap import is_air_gap_enabled, validate_air_gap_environment

@asynccontextmanager
async def lifespan(app: FastAPI):
    if is_air_gap_enabled():
        logger_name = "SQLAgent.AirGap"
        import logging
        logger = logging.getLogger(logger_name)
        logger.info("Air-Gapped Deployment Mode is ENABLED! Triggering startup verification...")
        try:
            validate_air_gap_environment()
            logger.info("Air-Gapped Startup verification PASSED.")
        except Exception as e:
            logger.error(f"Air-Gapped Startup verification FAILED: {e}")
            raise e
    yield

app = FastAPI(
    title="SQLAgent Mini Project API",
    description="A modular NL2SQL AI System",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(router, prefix="/api/v1")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "SQLAgent API is running."}
