"""
Shared fixtures for the OnlyFounders test suite.

* Spins up an async test database (postgresql+asyncpg)
* Overrides FastAPI's ``get_db`` dependency so every request uses the test session
* Provides reusable fixtures: authenticated client, test user, test startup, test agent
"""
from __future__ import annotations

import asyncio
import uuid
from typing import AsyncGenerator, Dict

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import get_db
from app.main import app
from app.models import Base

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:postgres@localhost:5432/onlyfounders_test"
)

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
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
# Create / drop tables once per session
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(event_loop):
    """Create all tables before tests run and drop them afterwards."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Per-test database session
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for each test."""
    async with TestSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# Dependency override
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(autouse=True)
async def override_get_db(db_session: AsyncSession):
    """Override the application ``get_db`` dependency with the test session."""

    async def _override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

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
