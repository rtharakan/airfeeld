"""
Airfeeld API Application

Main FastAPI application for the privacy-preserving aviation guessing game.

Security Features:
- Proof-of-work for bot prevention
- Rate limiting per endpoint
- OWASP security headers
- No cookies or persistent tracking
- SHA-256 hashed IP addresses
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import games_router, health_router, leaderboard_router, photos_router, players_router
from src.config import Settings, get_settings
from src.database import Database, set_database
from src.middleware.headers import SecurityHeadersMiddleware, get_cors_origins
from src.middleware.rate_limit import RateLimitMiddleware
from src.utils.errors import AirfeeldError
from src.utils.logging import get_logger, setup_logging

logger = get_logger(__name__)

# Global database instance
database: Database | None = None


def get_database() -> Database:
    """Get the global database instance."""
    if database is None:
        raise RuntimeError("Database not initialized")
    return database


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan manager.
    
    Handles startup and shutdown of database connections.
    """
    global database
    
    settings = get_settings()
    
    # Setup logging
    setup_logging()
    
    logger.info(
        f"Starting Airfeeld API v{settings.app_version} "
        f"({'debug' if settings.app_debug else 'production'} mode)"
    )
    
    # Initialize database
    database = Database(settings)
    await database.connect()
    
    # Make database available via app.state and globally
    app.state.database = database
    set_database(database)
    
    logger.info("Database connected")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")
    
    if database:
        await database.disconnect()
        logger.info("Database disconnected")


def create_app(settings: Settings | None = None) -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Args:
        settings: Optional settings override for testing
    
    Returns:
        Configured FastAPI application
    """
    settings = settings or get_settings()
    
    app = FastAPI(
        title="Airfeeld API",
        description=(
            "Privacy-preserving aviation guessing game. "
            "No accounts required. No tracking. Just fun."
        ),
        version=settings.app_version,
        docs_url="/docs" if settings.app_debug else None,
        redoc_url="/redoc" if settings.app_debug else None,
        openapi_url="/openapi.json" if settings.app_debug else None,
        lifespan=lifespan,
    )
    
    # Register exception handlers
    _register_exception_handlers(app)
    
    # Add middleware (order matters - last added is executed first)
    _add_middleware(app, settings)
    
    # Register routers
    _register_routers(app)
    
    return app


def _register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers."""
    
    @app.exception_handler(AirfeeldError)
    async def airfeeld_error_handler(
        request: Request, exc: AirfeeldError
    ) -> JSONResponse:
        """Handle application errors with appropriate status codes."""
        logger.warning(
            f"Application error: {exc.__class__.__name__} - {exc.message}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,
                "error_code": exc.__class__.__name__,
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle validation errors with clean messages."""
        # Extract field-level errors
        errors = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
            })
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Validation error",
                "errors": errors,
            },
        )
    
    @app.exception_handler(Exception)
    async def generic_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle unexpected errors without leaking details."""
        logger.exception(f"Unexpected error: {exc}")
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred",
            },
        )


def _add_middleware(app: FastAPI, settings: Settings) -> None:
    """Add middleware to the application."""
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(settings),
        allow_credentials=False,  # No cookies
        allow_methods=["GET", "POST", "DELETE"],
        allow_headers=["Content-Type", "X-Player-ID"],
        max_age=600,  # Cache preflight for 10 minutes
    )
    
    # Security headers middleware
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    
    # Rate limit middleware
    # Note: We add this after database is available via lifespan
    # For now, rate limiting is handled in individual endpoints


def _register_routers(app: FastAPI) -> None:
    """Register API routers."""
    
    # Health endpoints (no prefix)
    app.include_router(health_router)
    
    # Player management
    app.include_router(players_router)
    
    # Game endpoints
    app.include_router(games_router)
    
    # Photo endpoints
    app.include_router(photos_router)
    
    # Leaderboard
    app.include_router(leaderboard_router)


# Create the application instance
app = create_app()
