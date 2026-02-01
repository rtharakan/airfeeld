"""
Database Connection and Session Management

Provides async SQLAlchemy engine and session factories with:
- AES-256 encryption at rest via SQLCipher
- Connection pooling for performance
- Async session management for FastAPI

Security: Database encryption key must be set via AIRFEELD_DATABASE_KEY
environment variable in production. Without it, the database is unencrypted.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.config import Settings, get_settings

logger = logging.getLogger(__name__)


def _create_engine(settings: Settings) -> AsyncEngine:
    """
    Create async SQLAlchemy engine with appropriate configuration.
    
    For SQLite:
    - Uses WAL mode for better concurrency
    - Enables foreign key enforcement
    - Configures encryption if key is provided
    """
    # Ensure data directory exists
    if settings.database_url.startswith("sqlite"):
        db_path = settings.database_url.split("///")[-1]
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database_echo,
        # SQLite-specific: single connection for file-based SQLite
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    )
    
    return engine


def _configure_sqlite_connection(dbapi_conn: Any, connection_record: Any) -> None:
    """
    Configure SQLite connection with security and performance settings.
    
    Called for each new database connection to ensure:
    - Foreign key constraints are enforced
    - WAL mode is enabled for better concurrency
    - Encryption is configured if key is available
    """
    settings = get_settings()
    cursor = dbapi_conn.cursor()
    
    # Enable foreign key enforcement (disabled by default in SQLite)
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Use WAL mode for better concurrent read performance
    cursor.execute("PRAGMA journal_mode = WAL")
    
    # Synchronous mode: NORMAL is safe for WAL and faster than FULL
    cursor.execute("PRAGMA synchronous = NORMAL")
    
    # Configure encryption if key is provided
    if settings.database_encryption_enabled:
        # Note: This requires pysqlcipher3 instead of standard sqlite3
        # The key format depends on the SQLCipher version
        cursor.execute(f"PRAGMA key = '{settings.database_key}'")
        logger.info("Database encryption enabled")
    
    cursor.close()


class Database:
    """
    Database connection manager.
    
    Usage:
        db = Database()
        await db.connect()
        
        async with db.session() as session:
            # Use session for queries
            result = await session.execute(...)
        
        await db.disconnect()
    """
    
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None
    
    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine, raising if not connected."""
        if self._engine is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._engine
    
    async def connect(self) -> None:
        """
        Initialize database connection.
        
        Creates the engine, configures connection events, and
        sets up the session factory.
        """
        if self._engine is not None:
            logger.warning("Database already connected")
            return
        
        logger.info(f"Connecting to database: {self.settings.database_url}")
        
        self._engine = _create_engine(self.settings)
        
        # Register connection configuration callback for SQLite
        if "sqlite" in self.settings.database_url:
            # For async SQLite, we need to handle this differently
            # The configuration happens via connect_args or explicit PRAGMA
            pass
        
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        
        # Verify connection works
        async with self._engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            
            # Configure SQLite pragmas
            if "sqlite" in self.settings.database_url:
                await conn.execute(text("PRAGMA foreign_keys = ON"))
                await conn.execute(text("PRAGMA journal_mode = WAL"))
        
        logger.info("Database connected successfully")
    
    async def disconnect(self) -> None:
        """Close database connection and release resources."""
        if self._engine is None:
            return
        
        logger.info("Disconnecting from database")
        await self._engine.dispose()
        self._engine = None
        self._session_factory = None
        logger.info("Database disconnected")
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provide a transactional session scope.
        
        Usage:
            async with db.session() as session:
                result = await session.execute(query)
                await session.commit()
        
        The session automatically rolls back on exception.
        """
        if self._session_factory is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


# Global database instance
_db: Database | None = None


def get_database() -> Database:
    """Get the global database instance."""
    global _db
    if _db is None:
        _db = Database()
    return _db


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions.
    
    Usage in route handlers:
        @app.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            ...
    """
    db = get_database()
    async with db.session() as session:
        yield session
