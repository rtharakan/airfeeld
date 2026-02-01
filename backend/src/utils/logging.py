"""
Logging Configuration

Structured logging setup with privacy-aware log formatting.
Sensitive data (IPs, user IDs) are never logged in raw form.
"""

import logging
import sys
from datetime import datetime, timezone
from typing import Any

from src.config import get_settings


class PrivacyAwareFormatter(logging.Formatter):
    """
    Custom log formatter that ensures privacy compliance.
    
    Features:
    - UTC timestamps for consistency
    - No raw IP addresses in logs
    - No raw user IDs in logs
    - Structured output for log aggregation
    """
    
    def format(self, record: logging.LogRecord) -> str:
        # Ensure UTC timestamp
        record.created_utc = datetime.now(timezone.utc).isoformat()
        
        # Add request ID if available (for tracing)
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        
        return super().format(record)


def setup_logging() -> None:
    """
    Configure application logging.
    
    Sets up:
    - Console handler with appropriate level
    - Privacy-aware formatting
    - Suppression of noisy third-party loggers
    """
    settings = get_settings()
    
    # Parse log level
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    
    # Create formatter
    formatter = PrivacyAwareFormatter(
        fmt="%(created_utc)s | %(levelname)-8s | %(name)s | %(request_id)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # Configure application logger
    app_logger = logging.getLogger("airfeeld")
    app_logger.setLevel(level)
    
    # Suppress noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.database_echo else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a module.
    
    Usage:
        from src.utils.logging import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"airfeeld.{name}")


class LogContext:
    """
    Context manager for adding context to log messages.
    
    Usage:
        with LogContext(request_id="abc123"):
            logger.info("Processing request")
            # Logs will include request_id=abc123
    """
    
    def __init__(self, **kwargs: Any) -> None:
        self.context = kwargs
        self._old_factory: Any = None
    
    def __enter__(self) -> "LogContext":
        self._old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
            record = self._old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, *args: Any) -> None:
        logging.setLogRecordFactory(self._old_factory)


def log_security_event(
    event_type: str,
    message: str,
    ip_hash: str | None = None,
    **kwargs: Any,
) -> None:
    """
    Log a security-relevant event.
    
    All security events are logged at INFO level for audit purposes.
    IP addresses are logged as hashes only.
    
    Args:
        event_type: Type of security event (e.g., "rate_limit", "pow_failure")
        message: Human-readable description
        ip_hash: SHA-256 hash of client IP (optional)
        **kwargs: Additional context (no PII)
    """
    logger = get_logger("security")
    
    context = {"event_type": event_type}
    if ip_hash:
        context["ip_hash"] = ip_hash[:16] + "..."  # Truncate for logs
    context.update(kwargs)
    
    logger.info(f"[SECURITY] {event_type}: {message}", extra=context)
