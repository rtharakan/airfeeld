"""
Pytest Configuration and Fixtures

Shared test fixtures for all test modules.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.config import Settings
from src.models import Base


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings."""
    return Settings(
        app_debug=True,
        database_url="sqlite+aiosqlite:///:memory:",
        pow_difficulty=2,  # Lower for faster tests
        pow_reduced_difficulty=1,
        pow_challenge_ttl=300,
        pow_max_attempts_per_ip=100,
        rate_limit_enabled=True,
    )


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session_maker() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


@pytest.fixture
def mock_settings() -> MagicMock:
    """Create a mock settings object."""
    settings = MagicMock(spec=Settings)
    settings.app_debug = True
    settings.app_version = "0.1.0"
    settings.database_url = "sqlite+aiosqlite:///:memory:"
    settings.pow_difficulty = 4
    settings.pow_reduced_difficulty = 2
    settings.pow_challenge_ttl = 300
    settings.pow_max_attempts_per_ip = 10
    settings.rate_limit_enabled = True
    return settings


def pytest_configure(config: Any) -> None:
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks integration tests"
    )
    config.addinivalue_line(
        "markers", "security: marks security-focused tests"
    )
