"""Tests for /api/v1/startups/{startup_id}/traction — get (empty), upsert, get (with data)."""
from __future__ import annotations

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_traction_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /traction/ returns 404 when no traction metrics exist."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upsert_traction_create(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /traction/ creates traction metrics on first call."""
    payload = {
        "has_users": True,
        "active_users": 5000,
        "total_registered_users": 20000,
        "paying_customers": 500,
        "user_growth_rate_pct": 15.5,
        "has_revenue": True,
        "mrr": 5000000,
        "arr": 60000000,
        "north_star_metric_name": "weekly active users",
        "north_star_metric_value": "5000",
        "ltv_cents": 250000,
        "cac_cents": 50000,
        "key_milestones": "Launched beta",
    }
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_users"] is True
    assert data["active_users"] == 5000
    assert data["mrr"] == 5000000
    assert data["ltv_cents"] == 250000
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_upsert_traction_update(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /traction/ updates existing traction metrics."""
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        json={"has_users": False, "active_users": 0},
        headers=auth_user["headers"],
    )
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        json={"has_users": True, "active_users": 100},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["has_users"] is True
    assert data["active_users"] == 100


@pytest.mark.asyncio
async def test_get_traction_with_data(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """After upsert, GET /traction/ returns the saved data."""
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        json={"key_milestones": "Series A closed"},
        headers=auth_user["headers"],
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["key_milestones"] == "Series A closed"


@pytest.mark.asyncio
async def test_traction_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/traction/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_traction_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot access traction metrics."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/traction/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
