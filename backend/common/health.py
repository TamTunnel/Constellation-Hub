"""
Health check endpoints for Constellation Hub services.

Provides liveness (/healthz) and readiness (/readyz) probes
for Kubernetes and load balancer health checks.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .config import get_settings


router = APIRouter(tags=["Health"])


@router.get("/healthz")
async def liveness():
    """
    Liveness probe - indicates the service is running.
    
    Returns 200 if the service process is alive.
    Used by Kubernetes to determine if the pod should be restarted.
    
    This endpoint does NOT require authentication.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/readyz")
async def readiness(db: Optional[AsyncSession] = None):
    """
    Readiness probe - indicates the service is ready to accept traffic.
    
    Checks that the database connection is working.
    Returns 200 if ready, 503 if not.
    
    This endpoint does NOT require authentication.
    """
    settings = get_settings()
    checks = {
        "database": "unknown"
    }
    all_ready = True
    
    # Check database (if session provided)
    if db is not None:
        try:
            await db.execute(text("SELECT 1"))
            checks["database"] = "connected"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            all_ready = False
    else:
        checks["database"] = "not_configured"
    
    status_code = 200 if all_ready else 503
    
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if all_ready else "not_ready",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": checks
        }
    )


def create_health_router_with_db(get_db_dependency) -> APIRouter:
    """
    Create a health router with database dependency injection.
    
    Args:
        get_db_dependency: FastAPI dependency for getting DB session
        
    Returns:
        APIRouter with health endpoints configured for DB checks
    """
    health_router = APIRouter(tags=["Health"])
    
    @health_router.get("/healthz")
    async def liveness():
        return {
            "status": "ok",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    @health_router.get("/readyz")
    async def readiness(db: AsyncSession = Depends(get_db_dependency)):
        checks = {}
        all_ready = True
        
        # Check database
        try:
            await db.execute(text("SELECT 1"))
            checks["database"] = "connected"
        except Exception as e:
            checks["database"] = f"error: {str(e)}"
            all_ready = False
        
        status_code = 200 if all_ready else 503
        
        return JSONResponse(
            status_code=status_code,
            content={
                "status": "ready" if all_ready else "not_ready",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "checks": checks
            }
        )
    
    return health_router
