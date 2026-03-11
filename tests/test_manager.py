"""Tests for /api/v1/startups/{startup_id}/chat — Manager agent chat."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_manager_not_configured(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /chat/messages returns 503 when no manager agent exists in registry.

    NOTE: This test relies on the manager agent not already existing.
    We create a startup *without* the manager_agent fixture to test the error path.
    """
    # Create a startup fresh (the manager might or might not exist from other tests)
    # Instead, we test with a startup whose team does not have a manager.
    # If the manager agent exists in registry but is not on this startup's team,
    # it should return 404.
    startup_resp = await client.post(
        "/api/v1/startups/",
        json={"name": f"NoManagerStartup-{uuid.uuid4().hex[:6]}"},
        headers=auth_user["headers"],
    )
    startup_id = startup_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/startups/{startup_id}/chat/messages",
        headers=auth_user["headers"],
    )
    # Either 503 (manager not configured) or 404 (manager not on team)
    assert resp.status_code in (503, 404)


@pytest.mark.asyncio
async def test_manager_get_messages(
    client: AsyncClient, auth_user: Dict, manager_agent: Dict
):
    """GET /chat/messages returns messages when manager is on team.

    The manager is auto-assigned on startup creation when it exists.
    """
    # Create a startup AFTER the manager agent exists -> it gets auto-assigned
    startup_resp = await client.post(
        "/api/v1/startups/",
        json={"name": f"WithManager-{uuid.uuid4().hex[:6]}"},
        headers=auth_user["headers"],
    )
    assert startup_resp.status_code == 201
    startup_id = startup_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/startups/{startup_id}/chat/messages",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_manager_invoke(
    client: AsyncClient, auth_user: Dict, manager_agent: Dict
):
    """POST /chat/invoke sends a user message and receives a placeholder assistant response."""
    startup_resp = await client.post(
        "/api/v1/startups/",
        json={"name": f"InvokeManager-{uuid.uuid4().hex[:6]}"},
        headers=auth_user["headers"],
    )
    startup_id = startup_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/startups/{startup_id}/chat/invoke",
        json={"content": "Hello, Manager!"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "assistant"
    assert data["content"] is not None
    assert data["agent_id"] == manager_agent["id"]
    assert data["startup_id"] == startup_id


@pytest.mark.asyncio
async def test_manager_messages_after_invoke(
    client: AsyncClient, auth_user: Dict, manager_agent: Dict
):
    """After invoking the manager, GET /chat/messages includes both user and assistant messages."""
    startup_resp = await client.post(
        "/api/v1/startups/",
        json={"name": f"MsgsAfterInvoke-{uuid.uuid4().hex[:6]}"},
        headers=auth_user["headers"],
    )
    startup_id = startup_resp.json()["id"]

    await client.post(
        f"/api/v1/startups/{startup_id}/chat/invoke",
        json={"content": "What should I do next?"},
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{startup_id}/chat/messages",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    messages = resp.json()
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles


@pytest.mark.asyncio
async def test_manager_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated access to manager chat returns 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/chat/messages"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_manager_forbidden_non_member(
    client: AsyncClient,
    auth_user: Dict,
    auth_user2: Dict,
    manager_agent: Dict,
):
    """Non-member cannot invoke manager chat."""
    startup_resp = await client.post(
        "/api/v1/startups/",
        json={"name": f"ForbiddenManager-{uuid.uuid4().hex[:6]}"},
        headers=auth_user["headers"],
    )
    startup_id = startup_resp.json()["id"]

    resp = await client.post(
        f"/api/v1/startups/{startup_id}/chat/invoke",
        json={"content": "Trying to access"},
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
