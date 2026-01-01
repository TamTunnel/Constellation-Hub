"""
Structured logging for Constellation Hub services.

Provides JSON-formatted logs with consistent fields for observability.
"""
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import json
from contextvars import ContextVar

from .config import get_settings

# Context variable for request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class JSONFormatter(logging.Formatter):
    """JSON log formatter for production environments."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": getattr(record, "service", "unknown"),
            "message": record.getMessage(),
            "logger": record.name,
        }
        
        # Add request ID if available
        req_id = request_id_var.get()
        if req_id:
            log_data["request_id"] = req_id
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable formatter for local development."""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        service = getattr(record, "service", "unknown")
        req_id = request_id_var.get()
        
        prefix = f"{timestamp} [{record.levelname}] [{service}]"
        if req_id:
            prefix = f"{prefix} [{req_id[:8]}]"
        
        return f"{prefix} {record.getMessage()}"


class ServiceLogger(logging.Logger):
    """Custom logger that includes service context."""
    
    def __init__(self, name: str, service_name: str, level: int = logging.NOTSET):
        super().__init__(name, level)
        self.service_name = service_name
    
    def _log(self, level, msg, args, exc_info=None, extra=None, **kwargs):
        if extra is None:
            extra = {}
        extra["service"] = self.service_name
        super()._log(level, msg, args, exc_info=exc_info, extra=extra, **kwargs)
    
    def with_context(self, **kwargs) -> "ServiceLogger":
        """Return a logger adapter with additional context."""
        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                extra = kwargs.get("extra", {})
                extra["extra_fields"] = self.extra
                kwargs["extra"] = extra
                return msg, kwargs
        
        return ContextAdapter(self, kwargs)


def get_logger(service_name: str) -> ServiceLogger:
    """
    Get a configured logger for a service.
    
    Args:
        service_name: Name of the service (e.g., "core-orbits", "routing")
        
    Returns:
        Configured ServiceLogger instance
    """
    settings = get_settings()
    
    # Create logger
    logger = ServiceLogger(f"constellation.{service_name}", service_name)
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter based on config
    if settings.log_format == "json":
        handler.setFormatter(JSONFormatter())
    else:
        handler.setFormatter(TextFormatter())
    
    logger.addHandler(handler)
    
    return logger


def set_request_id(request_id: str) -> None:
    """Set the current request ID for logging context."""
    request_id_var.set(request_id)


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return request_id_var.get()
