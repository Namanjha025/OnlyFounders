"""Tests for /api/v1/startups/{startup_id}/equity — CRUD for shareholders."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_shareholders_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /equity/ returns an empty list initially."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_shareholder(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /equity/ creates a shareholder entry."""
    payload = {
        "name": "Founder A",
        "relationship_type": "founder",
        "equity_percentage": 45.00,
        "share_class": "common",
        "shares_owned": 4500000,
        "vesting_schedule": "4 years, 1 year cliff",
        "investment_amount": 0,
        "notes": "Co-founder",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Founder A"
    assert float(data["equity_percentage"]) == 45.00
    assert data["shares_owned"] == 4500000
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_create_shareholder_missing_name(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /equity/ without required 'name' returns 422."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        json={"equity_percentage": 10.0},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_shareholder(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /equity/{entry_id} updates a shareholder."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        json={"name": "Investor B", "equity_percentage": 10.0},
        headers=auth_user["headers"],
    )
    entry_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/equity/{entry_id}",
        json={"equity_percentage": 12.5, "notes": "Increased stake"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert float(resp.json()["equity_percentage"]) == 12.5
    assert resp.json()["notes"] == "Increased stake"


@pytest.mark.asyncio
async def test_update_shareholder_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /equity/{bad_id} returns 404."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/equity/{uuid.uuid4()}",
        json={"name": "Ghost"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_shareholder(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /equity/{entry_id} removes the shareholder."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        json={"name": "Temp Investor"},
        headers=auth_user["headers"],
    )
    entry_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/equity/{entry_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_shareholder_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /equity/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/equity/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_equity_forbidden_non_owner(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-owner cannot manage equity."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403

    resp2 = await client.post(
        f"/api/v1/startups/{test_startup['id']}/equity/",
        json={"name": "Hacker"},
        headers=auth_user2["headers"],
    )
    assert resp2.status_code == 403
