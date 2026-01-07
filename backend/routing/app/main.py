"""
FastAPI application for the Routing service.
Provides APIs for link management and path computation.
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
from .db import init_db, get_db

# Import from common module
try:
    from common.logger import get_logger, set_request_id
    from common.metrics import setup_metrics
    from common.health import create_health_router_with_db
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    def set_request_id(x): pass
    def setup_metrics(app, name): pass
    def create_health_router_with_db(dep): 
        from fastapi import APIRouter
        return APIRouter()

SERVICE_NAME = "routing"
logger = get_logger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting Routing service...")
    await init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down Routing service...")


app = FastAPI(
    title="Routing Service",
    description="Link modeling and path computation for Constellation Hub",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    set_request_id(request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Set up Prometheus metrics
setup_metrics(app, SERVICE_NAME)

# Include health check routes
health_router = create_health_router_with_db(get_db)
app.include_router(health_router)

# Include main routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint (legacy)."""
    return {"status": "healthy", "service": SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
