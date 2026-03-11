"""Tests for /api/v1/startups/{startup_id}/members — CRUD for team members."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_members(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /members/ includes the auto-created founder member."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    members = resp.json()
    assert isinstance(members, list)
    assert len(members) >= 1
    roles = [m["role"] for m in members]
    assert "founder" in roles


@pytest.mark.asyncio
async def test_add_member(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /members/ adds a new team member."""
    payload = {
        "name": "Alice Engineer",
        "email": "alice@example.com",
        "role": "cto",
        "title": "CTO",
        "department": "Engineering",
        "employment_type": "full_time",
        "is_full_time": True,
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Alice Engineer"
    assert data["role"] == "cto"
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_update_member(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /members/{member_id} updates the member."""
    # First add a member
    add_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/",
        json={"name": "Bob", "role": "employee", "title": "Dev"},
        headers=auth_user["headers"],
    )
    assert add_resp.status_code == 201
    member_id = add_resp.json()["id"]

    # Update
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}",
        json={"title": "Senior Dev", "department": "Platform"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Senior Dev"
    assert data["department"] == "Platform"


@pytest.mark.asyncio
async def test_update_member_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /members/{bad_id} returns 404."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/members/{uuid.uuid4()}",
        json={"title": "Ghost"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_member(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /members/{member_id} removes the member."""
    add_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/",
        json={"name": "Temp", "role": "employee"},
        headers=auth_user["headers"],
    )
    member_id = add_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_member_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /members/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/members/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_add_member_forbidden_for_non_owner(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-owner cannot add members."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/",
        json={"name": "Hacker", "role": "employee"},
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_add_member_missing_role(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /members/ without required 'role' returns 422."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/",
        json={"name": "NoRole"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 422
