"""Tests for /api/v1/startups — create, list mine, get, update."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_startup(client: AsyncClient, auth_user: Dict):
    """POST /startups/ creates a startup with slug and returns 201."""
    payload = {
        "name": "Acme Corp",
        "tagline": "Build the future",
        "stage": "seed",
        "industry": "fintech",
    }
    resp = await client.post(
        "/api/v1/startups/", json=payload, headers=auth_user["headers"]
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Acme Corp"
    assert data["tagline"] == "Build the future"
    assert data["stage"] == "seed"
    assert data["industry"] == "fintech"
    assert data["created_by"] == auth_user["user"]["id"]
    assert "slug" in data
    assert data["slug"]  # non-empty


@pytest.mark.asyncio
async def test_create_startup_auto_slug(client: AsyncClient, auth_user: Dict):
    """Slug is auto-generated from the name."""
    resp = await client.post(
        "/api/v1/startups/",
        json={"name": "My Awesome Startup!"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    assert resp.json()["slug"] == "my-awesome-startup"


@pytest.mark.asyncio
async def test_create_startup_duplicate_slug_increments(
    client: AsyncClient, auth_user: Dict
):
    """Creating two startups with the same name produces unique slugs."""
    name = f"DupSlug-{uuid.uuid4().hex[:6]}"
    r1 = await client.post(
        "/api/v1/startups/", json={"name": name}, headers=auth_user["headers"]
    )
    r2 = await client.post(
        "/api/v1/startups/", json={"name": name}, headers=auth_user["headers"]
    )
    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r1.json()["slug"] != r2.json()["slug"]


@pytest.mark.asyncio
async def test_create_startup_auto_assigns_founder_member(
    client: AsyncClient, auth_user: Dict
):
    """Creating a startup auto-creates a StartupMember for the founder."""
    resp = await client.post(
        "/api/v1/startups/",
        json={"name": f"MemberCheck-{uuid.uuid4().hex[:6]}"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    startup_id = resp.json()["id"]

    members_resp = await client.get(
        f"/api/v1/startups/{startup_id}/members/", headers=auth_user["headers"]
    )
    assert members_resp.status_code == 200
    members = members_resp.json()
    founder_members = [m for m in members if m["role"] == "founder"]
    assert len(founder_members) >= 1
    assert founder_members[0]["user_id"] == auth_user["user"]["id"]


@pytest.mark.asyncio
async def test_create_startup_unauthenticated(client: AsyncClient):
    """POST /startups/ without auth returns 401."""
    resp = await client.post("/api/v1/startups/", json={"name": "Nope"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_startup_missing_name(client: AsyncClient, auth_user: Dict):
    """POST /startups/ without name returns 422."""
    resp = await client.post(
        "/api/v1/startups/", json={}, headers=auth_user["headers"]
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_my_startups(client: AsyncClient, auth_user: Dict, test_startup: Dict):
    """GET /startups/mine returns only the current user's startups."""
    resp = await client.get(
        "/api/v1/startups/mine", headers=auth_user["headers"]
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    ids = [s["id"] for s in data]
    assert test_startup["id"] in ids


@pytest.mark.asyncio
async def test_list_my_startups_empty_for_new_user(
    client: AsyncClient, auth_user2: Dict
):
    """A new user with no startups gets an empty list."""
    resp = await client.get(
        "/api/v1/startups/mine", headers=auth_user2["headers"]
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_get_startup(client: AsyncClient, auth_user: Dict, test_startup: Dict):
    """GET /startups/{startup_id} returns the startup."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_get_startup_not_found(client: AsyncClient, auth_user: Dict):
    """GET /startups/{bad_id} returns 404."""
    resp = await client.get(
        f"/api/v1/startups/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_startup(client: AsyncClient, auth_user: Dict, test_startup: Dict):
    """PUT /startups/{startup_id} updates fields."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}",
        json={"tagline": "Updated tagline", "team_size": 5},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["tagline"] == "Updated tagline"
    assert data["team_size"] == 5


@pytest.mark.asyncio
async def test_update_startup_name_changes_slug(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Updating the name also regenerates the slug."""
    new_name = f"NewName-{uuid.uuid4().hex[:6]}"
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}",
        json={"name": new_name},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == new_name
    # slug should be based on the new name
    assert new_name.lower().replace("-", "") in resp.json()["slug"].replace("-", "")


@pytest.mark.asyncio
async def test_update_startup_forbidden_for_non_owner(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Non-owner cannot update the startup."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}",
        json={"tagline": "hacked"},
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
