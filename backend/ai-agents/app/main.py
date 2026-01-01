"""
FastAPI application for the AI Agents service.
"""
import sys
import uuid
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Add common module to path
sys.path.insert(0, str(__file__).replace('/ai-agents/app/main.py', ''))

from .routes import router

# Import from common module
try:
    from common.logger import get_logger, set_request_id
    from common.metrics import setup_metrics
    from common.health import router as health_router
except ImportError:
    import logging
    def get_logger(name): return logging.getLogger(name)
    def set_request_id(x): pass
    def setup_metrics(app, name): pass
    from fastapi import APIRouter
    health_router = APIRouter()

SERVICE_NAME = "ai-agents"
logger = get_logger(SERVICE_NAME)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    logger.info("Starting AI Agents service...")
    yield
    logger.info("Shutting down AI Agents service...")


app = FastAPI(
    title="AI Agents Service",
    description="AI-powered scheduling optimization and operations co-pilot for Constellation Hub",
    version="1.0.0",
    lifespan=lifespan,
)

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

# Include health check routes (no DB in this service)
app.include_router(health_router)

# Include main routes
app.include_router(router)


@app.get("/health")
async def health_check():
    """Health check endpoint (legacy)."""
    return {"status": "healthy", "service": SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
