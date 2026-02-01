"""
Utils Package

Common utility functions and classes.

Modules:
- errors: Custom exception classes
- logging: Privacy-aware logging configuration
"""

from src.utils.errors import (
    AirfeeldError,
    ContentModerationError,
    DatabaseError,
    ExifProcessingError,
    NotFoundError,
    PhotoProcessingError,
    ProofOfWorkError,
    ProofOfWorkExpiredError,
    ProfanityError,
    RateLimitError,
    UsernameConflictError,
    UsernameValidationError,
    ValidationError,
)
from src.utils.logging import (
    LogContext,
    get_logger,
    log_security_event,
    setup_logging,
)

__all__ = [
    # Errors
    "AirfeeldError",
    "ContentModerationError",
    "DatabaseError",
    "ExifProcessingError",
    "NotFoundError",
    "PhotoProcessingError",
    "ProofOfWorkError",
    "ProofOfWorkExpiredError",
    "ProfanityError",
    "RateLimitError",
    "UsernameConflictError",
    "UsernameValidationError",
    "ValidationError",
    # Logging
    "LogContext",
    "get_logger",
    "log_security_event",
    "setup_logging",
]
