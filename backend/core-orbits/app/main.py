"""
FastAPI application for the Core Orbits service.
Provides APIs for satellite positions, constellations, and coverage.
"""
import sys
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Add common module to path (fallback for local run, handled by PYTHONPATH in Docker)
try:
    import common
except ImportError:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from .routes import router
from .demo_routes import router as demo_router
from .db import init_db, get_db

# Import from common module
try:
    from common.logger import get_logger, set_request_id
    from common.metrics import setup_metrics
    from common.health import create_health_router_with_db
    from common.config import get_settings
except ImportError:
    # Fallback for standalone testing
    import logging
    def get_logger(name): return logging.getLogger(name)
    def set_request_id(x): pass
    def setup_metrics(app, name): pass
    def create_health_router_with_db(dep): 
        from fastapi import APIRouter
        return APIRouter()
    class get_settings:
        auth_disabled = True

SERVICE_NAME = "core-orbits"
logger = get_logger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting Core Orbits service...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Core Orbits service...")


app = FastAPI(
    title="Core Orbits Service",
    description="Orbital mechanics, satellite positions, and coverage computation for Constellation Hub",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware for logging
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_id(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Set up Prometheus metrics
setup_metrics(app, SERVICE_NAME)

# Include health check routes (no auth required)
health_router = create_health_router_with_db(get_db)
app.include_router(health_router)

# Include main routes
app.include_router(router)
app.include_router(demo_router)

# Include TLE routes
try:
    from .tle_routes import router as tle_router
    app.include_router(tle_router)
    logger.info("TLE routes loaded")
except ImportError as e:
    logger.warning(f"TLE routes not available: {e}")

# Mount auth routes
try:
    from common.auth_routes import router as auth_router
    app.include_router(auth_router)
except ImportError:
    logger.warning("Auth routes not available - running without auth endpoints")



# Legacy health endpoint (kept for backward compatibility)
@app.get("/health")
async def health_check():
    """Health check endpoint (legacy)."""
    return {"status": "healthy", "service": SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

