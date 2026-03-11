"""Tests for /api/v1/startups/{startup_id}/funding-rounds — CRUD."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_funding_rounds_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /funding-rounds/ returns an empty list initially."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_funding_round(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /funding-rounds/ creates a funding round."""
    payload = {
        "round_type": "seed",
        "amount_raised": 200000000,
        "pre_money_valuation": 800000000,
        "post_money_valuation": 1000000000,
        "round_date": "2024-06-15",
        "lead_investor": "Sequoia Capital",
        "investors": [{"name": "Sequoia"}, {"name": "YC"}],
        "instrument_type": "SAFE",
        "notes": "First institutional round",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["round_type"] == "seed"
    assert data["amount_raised"] == 200000000
    assert data["lead_investor"] == "Sequoia Capital"
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_create_funding_round_missing_type(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /funding-rounds/ without round_type returns 422."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        json={"amount_raised": 100},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_funding_round(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /funding-rounds/{round_id} updates a funding round."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        json={"round_type": "pre_seed", "amount_raised": 50000000},
        headers=auth_user["headers"],
    )
    round_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/{round_id}",
        json={"amount_raised": 75000000, "lead_investor": "Angel Group"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["amount_raised"] == 75000000
    assert resp.json()["lead_investor"] == "Angel Group"


@pytest.mark.asyncio
async def test_update_funding_round_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /funding-rounds/{bad_id} returns 404."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/{uuid.uuid4()}",
        json={"amount_raised": 1},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_funding_round(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /funding-rounds/{round_id} removes the round."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        json={"round_type": "grant"},
        headers=auth_user["headers"],
    )
    round_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/{round_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_funding_round_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /funding-rounds/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_funding_rounds_forbidden_non_owner(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-owner cannot create or list funding rounds."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403

    resp2 = await client.post(
        f"/api/v1/startups/{test_startup['id']}/funding-rounds/",
        json={"round_type": "seed"},
        headers=auth_user2["headers"],
    )
    assert resp2.status_code == 403
