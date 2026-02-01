"""
Error Handling Utilities

Custom exception classes and error response formatting.
All errors are designed to be informative without leaking
sensitive information (security by design).
"""

from typing import Any


class AirfeeldError(Exception):
    """
    Base exception for all Airfeeld errors.
    
    Provides structured error information for API responses.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
    
    def to_dict(self) -> dict[str, Any]:
        """Convert error to API response format."""
        response = {
            "error": self.error_code,
            "message": self.message,
        }
        if self.details:
            response["details"] = self.details
        return response


# Authentication & Authorization Errors

class AuthenticationError(AirfeeldError):
    """Error during authentication process."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="authentication_error",
            status_code=401,
            details=details,
        )


class ProofOfWorkError(AirfeeldError):
    """Proof-of-work challenge failed."""
    
    def __init__(
        self,
        message: str = "Invalid proof-of-work solution",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="invalid_pow",
            status_code=422,
            details=details,
        )


class ChallengeExpiredError(ProofOfWorkError):
    """Proof-of-work challenge has expired."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Challenge has expired. Please request a new challenge.",
            details={"reason": "expired"},
        )


# Rate Limiting Errors

class RateLimitError(AirfeeldError):
    """Rate limit exceeded."""
    
    def __init__(
        self,
        retry_after_seconds: int,
        limit: int,
        window_seconds: int,
    ) -> None:
        super().__init__(
            message="Rate limit exceeded. Please try again later.",
            error_code="rate_limit_exceeded",
            status_code=429,
            details={
                "retry_after_seconds": retry_after_seconds,
                "limit": limit,
                "window_seconds": window_seconds,
            },
        )
        self.retry_after_seconds = retry_after_seconds


# Validation Errors

class ValidationError(AirfeeldError):
    """Request validation failed."""
    
    def __init__(
        self,
        message: str,
        field: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = details or {}
        if field:
            error_details["field"] = field
        
        super().__init__(
            message=message,
            error_code="validation_error",
            status_code=400,
            details=error_details,
        )


class UsernameValidationError(ValidationError):
    """Username validation failed."""
    
    def __init__(self, message: str = "Invalid username") -> None:
        super().__init__(
            message=message,
            field="username",
            details={
                "requirements": "3-20 characters, alphanumeric and underscore only",
            },
        )


class ProfanityError(ValidationError):
    """Username contains profanity."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Username contains inappropriate content",
            field="username",
        )


# Resource Errors

class NotFoundError(AirfeeldError):
    """Requested resource not found."""
    
    def __init__(
        self,
        resource_type: str,
        resource_id: str | None = None,
    ) -> None:
        message = f"{resource_type} not found"
        details = {"resource_type": resource_type}
        if resource_id:
            details["resource_id"] = resource_id
        
        super().__init__(
            message=message,
            error_code="not_found",
            status_code=404,
            details=details,
        )


class ConflictError(AirfeeldError):
    """Resource conflict (e.g., duplicate username)."""
    
    def __init__(
        self,
        message: str,
        field: str | None = None,
    ) -> None:
        details = {}
        if field:
            details["field"] = field
        
        super().__init__(
            message=message,
            error_code="conflict",
            status_code=409,
            details=details,
        )


class UsernameConflictError(ConflictError):
    """Username already taken."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Username already taken",
            field="username",
        )


# Gameplay Errors

class GameplayError(AirfeeldError):
    """Error during gameplay."""
    
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            error_code="gameplay_error",
            status_code=400,
            details=details,
        )


class RoundExpiredError(GameplayError):
    """Game round has expired."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Game round has expired",
            details={"reason": "expired"},
        )


class RoundNotFoundError(NotFoundError):
    """Game round not found."""
    
    def __init__(self, round_id: str | None = None) -> None:
        super().__init__(
            resource_type="Game round",
            resource_id=round_id,
        )


class InvalidTokenError(GameplayError):
    """Invalid round token."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Invalid round token",
            details={"reason": "invalid_token"},
        )


# Content Moderation Errors

class ContentModerationError(AirfeeldError):
    """Content failed moderation checks."""
    
    def __init__(
        self,
        message: str,
        reason: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        error_details = {"reason": reason}
        if details:
            error_details.update(details)
        
        super().__init__(
            message=message,
            error_code="content_rejected",
            status_code=422,
            details=error_details,
        )


class PhotoRejectedError(ContentModerationError):
    """Photo upload rejected by moderation."""
    
    def __init__(self, reason: str, message: str | None = None) -> None:
        super().__init__(
            message=message or f"Photo rejected: {reason}",
            reason=reason,
        )


# Photo Processing Errors

class PhotoProcessingError(AirfeeldError):
    """Error processing uploaded photo."""
    
    def __init__(self, message: str = "Failed to process photo") -> None:
        super().__init__(
            message=message,
            error_code="photo_processing_error",
            status_code=422,
        )


class PhotoValidationError(PhotoProcessingError):
    """Photo validation failed."""
    
    def __init__(self, message: str) -> None:
        super().__init__(message=message)
        self.error_code = "photo_validation_error"


class PhotoTooLargeError(PhotoProcessingError):
    """Photo file size exceeds limit."""
    
    def __init__(self, actual_size: int, max_size: int) -> None:
        super().__init__(
            message=f"Photo too large: {actual_size} bytes (max: {max_size})"
        )
        self.error_code = "photo_too_large"


class DuplicatePhotoError(PhotoProcessingError):
    """Photo is a duplicate of existing photo."""
    
    def __init__(self) -> None:
        super().__init__(message="This photo appears to be a duplicate")
        self.error_code = "duplicate_photo"


class ExifProcessingError(PhotoProcessingError):
    """Error processing photo EXIF data."""
    
    def __init__(self, message: str = "Failed to process photo metadata") -> None:
        super().__init__(message=message)
        self.error_code = "exif_processing_error"


# Game Errors

class GameRoundNotFoundError(NotFoundError):
    """Game round not found."""
    
    def __init__(self, round_id: str | None = None) -> None:
        super().__init__(
            resource_type="GameRound",
            resource_id=round_id,
        )


class RoundNotActiveError(GameplayError):
    """Game round is not active."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Game round is not active",
            details={"reason": "not_active"},
        )


class ProofOfWorkExpiredError(ProofOfWorkError):
    """Proof-of-work challenge has expired."""
    
    def __init__(self) -> None:
        super().__init__(
            message="Challenge has expired. Please request a new challenge.",
            details={"reason": "expired"},
        )


# Database Errors

class DatabaseError(ServerError):
    """Database operation failed."""
    
    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(message=message)
        self.error_code = "database_error"


# Server Errors

class ServerError(AirfeeldError):
    """Internal server error."""
    
    def __init__(
        self,
        message: str = "An unexpected error occurred",
        details: dict[str, Any] | None = None,
    ) -> None:
        # Never expose internal details in production
        super().__init__(
            message=message,
            error_code="server_error",
            status_code=500,
            details=details,
        )
