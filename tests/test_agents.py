"""Tests for agent endpoints: registry CRUD, add/remove from team, chat messages, invoke."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


# ============================================================
# Agent Registry — /api/v1/agents
# ============================================================


@pytest.mark.asyncio
async def test_list_agents_empty_or_populated(client: AsyncClient):
    """GET /agents/ returns a list (possibly empty at first)."""
    resp = await client.get("/api/v1/agents/")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient, auth_user: Dict):
    """POST /agents/ creates a new agent."""
    slug = f"agent-{uuid.uuid4().hex[:6]}"
    payload = {
        "name": "Test Agent",
        "slug": slug,
        "description": "A helpful agent",
        "agent_type": "platform",
        "system_prompt": "You are a helpful assistant.",
        "skills": ["coding", "analysis"],
    }
    resp = await client.post(
        "/api/v1/agents/", json=payload, headers=auth_user["headers"]
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test Agent"
    assert data["slug"] == slug
    assert data["agent_type"] == "platform"
    assert data["is_active"] is True
    assert data["skills"] == ["coding", "analysis"]


@pytest.mark.asyncio
async def test_create_agent_duplicate_slug(
    client: AsyncClient, auth_user: Dict, test_agent: Dict
):
    """POST /agents/ with an existing slug returns 400."""
    resp = await client.post(
        "/api/v1/agents/",
        json={"name": "Dup", "slug": test_agent["slug"]},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 400
    assert "slug already exists" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_agent_unauthenticated(client: AsyncClient):
    """POST /agents/ without auth returns 401."""
    resp = await client.post(
        "/api/v1/agents/",
        json={"name": "No Auth", "slug": "no-auth"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient, test_agent: Dict):
    """GET /agents/{agent_id} returns the agent."""
    resp = await client.get(f"/api/v1/agents/{test_agent['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == test_agent["id"]


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    """GET /agents/{bad_id} returns 404."""
    resp = await client.get(f"/api/v1/agents/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(
    client: AsyncClient, auth_user: Dict, test_agent: Dict
):
    """PUT /agents/{agent_id} updates the agent."""
    resp = await client.put(
        f"/api/v1/agents/{test_agent['id']}",
        json={"name": "Updated Agent", "description": "New description"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated Agent"
    assert resp.json()["description"] == "New description"


@pytest.mark.asyncio
async def test_update_agent_not_found(client: AsyncClient, auth_user: Dict):
    """PUT /agents/{bad_id} returns 404."""
    resp = await client.put(
        f"/api/v1/agents/{uuid.uuid4()}",
        json={"name": "Ghost"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_agent_deactivate(
    client: AsyncClient, auth_user: Dict, test_agent: Dict
):
    """PUT /agents/{agent_id} can deactivate an agent."""
    resp = await client.put(
        f"/api/v1/agents/{test_agent['id']}",
        json={"is_active": False},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False

    # Re-activate for other tests
    await client.put(
        f"/api/v1/agents/{test_agent['id']}",
        json={"is_active": True},
        headers=auth_user["headers"],
    )


# ============================================================
# Agent Team — /api/v1/startups/{startup_id}/agents
# ============================================================


@pytest.mark.asyncio
async def test_list_startup_agents(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /startups/{sid}/agents/ returns agent members (possibly empty)."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_add_agent_to_team(
    client: AsyncClient, auth_user: Dict, test_startup: Dict, test_agent: Dict
):
    """POST /startups/{sid}/agents/?agent_id={id} adds agent to team."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["agent_id"] == test_agent["id"]
    assert data["role"] == "employee"


@pytest.mark.asyncio
async def test_add_agent_to_team_already_on_team(
    client: AsyncClient, auth_user: Dict, test_startup: Dict, test_agent: Dict
):
    """Adding the same agent again returns 400."""
    # Add first
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user["headers"],
    )
    # Try again
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 400
    assert "already on team" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_add_nonexistent_agent_to_team(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Adding a nonexistent agent returns 404."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": str(uuid.uuid4())},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_remove_agent_from_team(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /startups/{sid}/agents/{agent_id} removes the agent from team."""
    # Create a fresh agent to add and remove
    slug = f"remove-{uuid.uuid4().hex[:6]}"
    agent_resp = await client.post(
        "/api/v1/agents/",
        json={"name": "Removable", "slug": slug},
        headers=auth_user["headers"],
    )
    agent_id = agent_resp.json()["id"]

    # Add to team
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": agent_id},
        headers=auth_user["headers"],
    )

    # Remove
    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/agents/{agent_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_remove_agent_not_on_team(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /startups/{sid}/agents/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/agents/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_agent_forbidden_non_owner(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict, test_agent: Dict
):
    """Non-owner cannot add agents to team."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403


# ============================================================
# Agent Chat — /api/v1/startups/{sid}/agents/{aid}/chat
# ============================================================


@pytest.mark.asyncio
async def test_get_agent_chat_messages_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict, test_agent: Dict
):
    """GET /chat/messages returns empty list when no messages exist.
    Agent must be on team first.
    """
    # Ensure agent is on team (may already be from previous test)
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/agents/{test_agent['id']}/chat/messages",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_invoke_agent(
    client: AsyncClient, auth_user: Dict, test_startup: Dict, test_agent: Dict
):
    """POST /chat/invoke sends a message and gets an assistant response."""
    # Ensure agent is on team
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user["headers"],
    )

    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/{test_agent['id']}/chat/invoke",
        json={"content": "Hello, agent!"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "assistant"
    assert data["content"] is not None
    assert data["agent_id"] == test_agent["id"]
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_invoke_agent_not_on_team(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /chat/invoke for an agent not on team returns 403."""
    fake_agent_id = str(uuid.uuid4())
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/{fake_agent_id}/chat/invoke",
        json={"content": "Hello?"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_get_messages_after_invoke(
    client: AsyncClient, auth_user: Dict, test_startup: Dict, test_agent: Dict
):
    """After invoking, GET /chat/messages returns the conversation."""
    # Ensure agent on team
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/",
        params={"agent_id": test_agent["id"]},
        headers=auth_user["headers"],
    )

    # Invoke
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/agents/{test_agent['id']}/chat/invoke",
        json={"content": "Test message"},
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/agents/{test_agent['id']}/chat/messages",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    messages = resp.json()
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles
