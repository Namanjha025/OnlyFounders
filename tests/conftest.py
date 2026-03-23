"""
Shared fixtures for the OnlyFounders test suite.

* Runs Alembic migrations (sync psycopg2) to set up the test database schema
* Overrides FastAPI's ``get_db`` dependency so every request uses the test session
* Provides reusable fixtures: authenticated client, test user, test startup, test agent
"""
from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import uuid
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.database import get_db
from app.main import app
from app.models import Base

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
TEST_DB_NAME = "onlyfounders_test"
TEST_DATABASE_URL = f"postgresql+asyncpg://sidda:postgres@localhost:5432/{TEST_DB_NAME}"

# IMPORTANT: Use NullPool to avoid connection sharing issues in tests.
# NullPool creates a new connection for each session instead of reusing
# connections from a pool, which prevents "another operation is in progress".
engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Session-scoped event loop
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop shared across all tests in the session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# Schema setup via Alembic (uses sync psycopg2 — avoids asyncpg enum issues)
# ---------------------------------------------------------------------------
def _psql(sql: str) -> None:
    subprocess.run(
        ["psql", "-U", "sidda", "-d", TEST_DB_NAME, "-c", sql],
        capture_output=True,
        env={**os.environ, "PGPASSWORD": "postgres"},
    )


def _clean_db() -> None:
    """Drop all tables and enum types."""
    _psql(
        "DO $$ DECLARE r RECORD; "
        "BEGIN "
        "FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP "
        "EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE'; "
        "END LOOP; "
        "FOR r IN (SELECT typname FROM pg_type WHERE typtype = 'e') LOOP "
        "EXECUTE 'DROP TYPE IF EXISTS ' || quote_ident(r.typname) || ' CASCADE'; "
        "END LOOP; "
        "END $$;"
    )


def _alembic_upgrade() -> None:
    env = os.environ.copy()
    env["DATABASE_URL"] = f"postgresql+asyncpg://sidda:postgres@localhost:5432/{TEST_DB_NAME}"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Alembic upgrade failed:\n{result.stderr}")


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(event_loop):
    """Run Alembic migration to set up the test database."""
    _clean_db()
    _alembic_upgrade()
    yield
    _clean_db()


# ---------------------------------------------------------------------------
# Dependency override — each endpoint call gets its own session
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def override_get_db():
    """Override ``get_db`` so every FastAPI dependency call gets a fresh session.

    This mirrors production behaviour where ``get_db`` opens (and closes) its
    own ``AsyncSession`` for each request.  Sharing a single session between
    the ASGI transport and the test coroutine would cause
    ``InterfaceError: another operation is in progress``.
    """

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        async with TestSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Async HTTP client
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """httpx AsyncClient wired to the FastAPI app via ASGITransport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _unique_email() -> str:
    return f"test-{uuid.uuid4().hex[:8]}@example.com"


# ---------------------------------------------------------------------------
# Authenticated user fixture
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def auth_user(client: AsyncClient) -> Dict:
    """Register a user and return dict with ``user``, ``token``, ``headers``."""
    email = _unique_email()
    payload = {
        "email": email,
        "password": "Test1234!",
        "first_name": "Test",
        "last_name": "User",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    token = data["access_token"]
    return {
        "user": data["user"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
        "email": email,
        "password": "Test1234!",
    }


# ---------------------------------------------------------------------------
# Second authenticated user (for access-control tests)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def auth_user2(client: AsyncClient) -> Dict:
    """Register a *second* user and return dict with ``user``, ``token``, ``headers``."""
    email = _unique_email()
    payload = {
        "email": email,
        "password": "Other1234!",
        "first_name": "Other",
        "last_name": "Person",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    token = data["access_token"]
    return {
        "user": data["user"],
        "token": token,
        "headers": {"Authorization": f"Bearer {token}"},
    }


# ---------------------------------------------------------------------------
# Test startup fixture
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_startup(client: AsyncClient, auth_user: Dict) -> Dict:
    """Create a startup owned by ``auth_user`` and return its JSON."""
    resp = await client.post(
        "/api/v1/startups/",
        json={
            "name": f"TestStartup-{uuid.uuid4().hex[:6]}",
            "tagline": "Test tagline",
            "stage": "idea",
            "industry": "saas",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Test agent fixture (in registry)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def test_agent(client: AsyncClient, auth_user: Dict) -> Dict:
    """Create an agent in the registry and return its JSON."""
    resp = await client.post(
        "/api/v1/agents/",
        json={
            "name": f"TestAgent-{uuid.uuid4().hex[:6]}",
            "slug": f"test-agent-{uuid.uuid4().hex[:6]}",
            "description": "An agent for testing",
            "agent_type": "platform",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# Manager agent fixture  (slug = "manager")
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def manager_agent(client: AsyncClient, auth_user: Dict) -> Dict:
    """Create the special Manager agent (slug='manager') in the registry."""
    slug = "manager"
    # First, check if manager already exists (idempotent)
    resp = await client.get("/api/v1/agents/")
    agents = resp.json()
    for a in agents:
        if a["slug"] == slug:
            return a
    resp = await client.post(
        "/api/v1/agents/",
        json={
            "name": "Manager",
            "slug": slug,
            "description": "The manager agent",
            "agent_type": "platform",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()
