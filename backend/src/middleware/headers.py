"""
Security Headers Middleware

Adds standard security headers to all responses.
Implements OWASP recommended security headers.

Headers Added:
- X-Content-Type-Options: Prevent MIME sniffing
- X-Frame-Options: Prevent clickjacking
- X-XSS-Protection: Legacy XSS protection
- Content-Security-Policy: Restrict resource loading
- Referrer-Policy: Control referrer information
- Strict-Transport-Security: Enforce HTTPS (production only)
- Permissions-Policy: Restrict browser features
"""

from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.config import Settings, get_settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware that adds security headers to all responses.
    
    Configurable for development vs production environments.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        settings: Settings | None = None,
    ) -> None:
        """
        Initialize security headers middleware.
        
        Args:
            app: ASGI application
            settings: Application settings (uses defaults if not provided)
        """
        super().__init__(app)
        self.settings = settings or get_settings()
        self.headers = self._build_headers()
    
    def _build_headers(self) -> dict[str, str]:
        """
        Build security headers based on environment.
        
        Returns:
            Dictionary of header name to value
        """
        headers = {
            # Prevent MIME type sniffing
            "X-Content-Type-Options": "nosniff",
            
            # Prevent embedding in frames (clickjacking protection)
            "X-Frame-Options": "DENY",
            
            # Legacy XSS protection (modern browsers use CSP)
            "X-XSS-Protection": "1; mode=block",
            
            # Control referrer information
            "Referrer-Policy": "strict-origin-when-cross-origin",
            
            # Restrict browser features
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=()"
            ),
            
            # Content Security Policy
            "Content-Security-Policy": self._build_csp(),
        }
        
        # Add HSTS in production
        if not self.settings.app_debug:
            headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )
        
        return headers
    
    def _build_csp(self) -> str:
        """
        Build Content-Security-Policy header.
        
        Restrictive policy suitable for an API backend.
        """
        directives = [
            "default-src 'none'",
            "frame-ancestors 'none'",
            "form-action 'none'",
            "base-uri 'none'",
        ]
        
        # Allow self for script/style in docs
        if self.settings.app_debug:
            directives.extend([
                "script-src 'self' 'unsafe-inline'",
                "style-src 'self' 'unsafe-inline'",
                "img-src 'self' data:",
            ])
        
        return "; ".join(directives)
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Any],
    ) -> Response:
        """
        Add security headers to response.
        """
        response = await call_next(request)
        
        # Add all security headers
        for name, value in self.headers.items():
            response.headers[name] = value
        
        return response


def get_cors_origins(settings: Settings | None = None) -> list[str]:
    """
    Get allowed CORS origins based on environment.
    
    Args:
        settings: Application settings
    
    Returns:
        List of allowed origin URLs
    """
    settings = settings or get_settings()
    
    if settings.app_debug:
        # Allow localhost in development
        return [
            "http://localhost:3000",
            "http://localhost:5173",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
    
    # Production: require explicit origins
    # TODO: Load from environment variable
    return []
