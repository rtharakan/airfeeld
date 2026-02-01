"""
Rate Limit Middleware

FastAPI middleware for API rate limiting.
Checks rate limits before request processing and adds headers to responses.

Features:
- Per-endpoint rate limits
- IP-based tracking (hashed for privacy)
- Standard X-RateLimit headers
- Configurable limits per endpoint
"""

from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.database import Database
from src.models.rate_limit import get_rate_limit
from src.services.rate_limit_service import (
    RateLimitService,
    get_rate_limit_headers,
)
from src.utils.errors import RateLimitError
from src.utils.logging import get_logger

logger = get_logger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Extract client IP from request.
    
    Handles X-Forwarded-For header for proxy environments.
    """
    # Check for proxy headers first
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP in the chain (original client)
        return forwarded.split(",")[0].strip()
    
    # Fall back to direct connection IP
    if request.client:
        return request.client.host
    
    return "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces rate limits on API endpoints.
    
    Rate limits are configurable per endpoint. Requests exceeding
    the limit receive a 429 response with Retry-After header.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        database: Database,
        exclude_paths: list[str] | None = None,
    ) -> None:
        """
        Initialize rate limit middleware.
        
        Args:
            app: ASGI application
            database: Database instance for session management
            exclude_paths: Paths to exclude from rate limiting
        """
        super().__init__(app)
        self.database = database
        self.rate_limit_service = RateLimitService()
        self.exclude_paths = exclude_paths or [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Any],
    ) -> Response:
        """
        Process request with rate limiting.
        
        Checks rate limit before processing. On limit exceeded,
        returns 429 response. Otherwise, adds rate limit headers
        to the response.
        """
        path = request.url.path
        
        # Skip excluded paths
        if self._is_excluded(path):
            return await call_next(request)
        
        # Get endpoint key for rate limiting
        endpoint = self._get_endpoint_key(path)
        if not endpoint:
            return await call_next(request)
        
        client_ip = get_client_ip(request)
        
        try:
            async with self.database.session() as session:
                # Check rate limit
                await self.rate_limit_service.check_rate_limit(
                    session, client_ip, endpoint
                )
                
                # Get current usage for headers
                remaining, reset_time = await self.rate_limit_service.get_remaining(
                    session, client_ip, endpoint
                )
                
                # Process request
                response = await call_next(request)
                
                # Add rate limit headers
                limit_config = get_rate_limit(endpoint)
                if limit_config:
                    headers = get_rate_limit_headers(
                        limit=limit_config["limit"],
                        remaining=remaining,
                        reset_timestamp=int(reset_time.timestamp()) if reset_time else 0,
                    )
                    for key, value in headers.items():
                        response.headers[key] = value
                
                return response
                
        except RateLimitError as e:
            logger.warning(
                f"Rate limit exceeded: endpoint={endpoint}, "
                f"retry_after={e.retry_after}"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": e.message,
                    "retry_after": e.retry_after,
                },
                headers={"Retry-After": str(e.retry_after)},
            )
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path is excluded from rate limiting."""
        for excluded in self.exclude_paths:
            if path.startswith(excluded):
                return True
        return False
    
    def _get_endpoint_key(self, path: str) -> str | None:
        """
        Map URL path to rate limit endpoint key.
        
        Returns None if path is not rate limited.
        """
        # Map paths to endpoint keys
        path_mappings = {
            "/players/challenge": "/players/challenge",
            "/players/register": "/players/register",
            "/photos": "/photos",
            "/games": "/games",
            "/guesses": "/guesses",
        }
        
        for prefix, endpoint in path_mappings.items():
            if path.startswith(prefix):
                return endpoint
        
        return None
