"""Tests for /api/v1/startups/{startup_id}/financials — get (empty), upsert, get (with data)."""
from __future__ import annotations

from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_financials_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /financials/ returns 404 when no financial details exist."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_upsert_financials_create(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /financials/ creates financial details on first call."""
    payload = {
        "monthly_burn_rate": 5000000,
        "cash_in_bank": 100000000,
        "runway_months": 20,
        "monthly_revenue": 2000000,
        "monthly_expenses": 5000000,
        "gross_margin_pct": 70.0,
        "is_fundraising": True,
        "fundraise_target": 500000000,
        "fundraise_round_type": "seed",
        "total_raised": 200000000,
    }
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["monthly_burn_rate"] == 5000000
    assert data["cash_in_bank"] == 100000000
    assert data["runway_months"] == 20
    assert data["is_fundraising"] is True
    assert data["fundraise_round_type"] == "seed"
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_upsert_financials_update(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /financials/ updates existing financial details."""
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        json={"monthly_burn_rate": 1000000},
        headers=auth_user["headers"],
    )
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        json={"monthly_burn_rate": 2000000, "runway_months": 18},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["monthly_burn_rate"] == 2000000
    assert data["runway_months"] == 18


@pytest.mark.asyncio
async def test_get_financials_with_data(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """After upsert, GET /financials/ returns the saved data."""
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        json={"total_raised": 9999999},
        headers=auth_user["headers"],
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["total_raised"] == 9999999


@pytest.mark.asyncio
async def test_financials_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/financials/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_financials_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot access financial details."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/financials/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
