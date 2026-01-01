"""
Prometheus metrics for Constellation Hub services.

Provides standardized metrics collection for request counting, latency, and errors.
"""
from typing import Callable
import time

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from .config import get_settings


# Request metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["service", "method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

ERROR_COUNT = Counter(
    "errors_total",
    "Total error count",
    ["service", "error_type"]
)

# Custom business metrics
SATELLITES_TRACKED = Counter(
    "satellites_tracked_total",
    "Total satellites tracked",
    ["constellation"]
)

PASSES_COMPUTED = Counter(
    "passes_computed_total",
    "Total visibility passes computed",
    ["service"]
)

SCHEDULES_GENERATED = Counter(
    "schedules_generated_total",
    "Total schedules generated",
    ["service", "optimizer"]
)


def get_metrics_response() -> Response:
    """Generate Prometheus metrics response."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


def create_metrics_middleware(service_name: str) -> Callable:
    """
    Create FastAPI middleware for collecting request metrics.

    Args:
        service_name: Name of the service for metric labels

    Returns:
        Middleware function
    """
    async def metrics_middleware(request: Request, call_next):
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Time the request
        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            # Record error
            ERROR_COUNT.labels(
                service=service_name,
                error_type=type(e).__name__
            ).inc()
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time
            endpoint = request.url.path
            method = request.method

            REQUEST_COUNT.labels(
                service=service_name,
                method=method,
                endpoint=endpoint,
                status_code=status_code if 'status_code' in dir() else 500
            ).inc()

            REQUEST_LATENCY.labels(
                service=service_name,
                method=method,
                endpoint=endpoint
            ).observe(duration)

        return response

    return metrics_middleware


def setup_metrics(app: FastAPI, service_name: str) -> None:
    """
    Set up Prometheus metrics for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
    """
    settings = get_settings()

    if not settings.metrics_enabled:
        return

    # Add metrics endpoint
    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return get_metrics_response()

    # Add middleware
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next):
        middleware_fn = create_metrics_middleware(service_name)
        return await middleware_fn(request, call_next)
