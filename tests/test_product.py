"""Tests for /api/v1/startups/{startup_id}/product — get (empty), upsert, get (with data)."""
from __future__ import annotations

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_product_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /product/ returns 404 when no product details exist."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/product/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upsert_product_create(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /product/ creates product details on first call."""
    payload = {
        "problem": "Manual data entry is slow",
        "solution": "AI-powered automation",
        "product_stage": "mvp",
        "target_audience": "SMBs",
        "tam": 5000000000,
        "sam": 1000000000,
        "som": 100000000,
        "competitive_advantage": "First mover",
        "revenue_model": "SaaS subscription",
        "tech_stack": ["Python", "React"],
        "competitors": [{"name": "CompA", "strength": "Brand"}],
    }
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/product/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["problem"] == "Manual data entry is slow"
    assert data["product_stage"] == "mvp"
    assert data["tam"] == 5000000000
    assert data["tech_stack"] == ["Python", "React"]
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_upsert_product_update(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /product/ updates existing product details."""
    # Create
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/product/",
        json={"problem": "Original problem"},
        headers=auth_user["headers"],
    )
    # Update
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/product/",
        json={"problem": "Refined problem", "solution": "New solution"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["problem"] == "Refined problem"
    assert data["solution"] == "New solution"


@pytest.mark.asyncio
async def test_get_product_with_data(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """After upsert, GET /product/ returns the saved data."""
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/product/",
        json={"problem": "get-test", "why_now": "Market timing"},
        headers=auth_user["headers"],
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/product/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["why_now"] == "Market timing"


@pytest.mark.asyncio
async def test_product_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests to product endpoints return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/product/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_product_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot access product details."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/product/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
