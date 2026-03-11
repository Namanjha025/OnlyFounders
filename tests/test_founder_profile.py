"""Tests for /api/v1/profile — get/update founder profile."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_my_profile_not_found(client: AsyncClient, auth_user: Dict):
    """GET /profile/me returns 404 when no profile exists yet."""
    resp = await client.get("/api/v1/profile/me", headers=auth_user["headers"])
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_and_get_profile(client: AsyncClient, auth_user: Dict):
    """PUT /profile/me creates the profile, GET /profile/me returns it."""
    update_payload = {
        "phone": "+1234567890",
        "bio": "Serial entrepreneur",
        "linkedin_url": "https://linkedin.com/in/test",
        "city": "San Francisco",
        "country": "US",
        "is_technical": True,
        "is_full_time": True,
        "education": "Stanford",
        "degree_field": "CS",
        "years_of_experience": 10,
        "skills": ["python", "leadership"],
        "domain_expertise": ["saas", "fintech"],
    }
    put_resp = await client.put(
        "/api/v1/profile/me", json=update_payload, headers=auth_user["headers"]
    )
    assert put_resp.status_code == 200
    profile = put_resp.json()
    assert profile["phone"] == "+1234567890"
    assert profile["bio"] == "Serial entrepreneur"
    assert profile["user_id"] == auth_user["user"]["id"]
    assert profile["is_technical"] is True
    assert profile["skills"] == ["python", "leadership"]

    get_resp = await client.get("/api/v1/profile/me", headers=auth_user["headers"])
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == profile["id"]


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient, auth_user: Dict):
    """PUT /profile/me with partial data only updates provided fields."""
    # Create first
    await client.put(
        "/api/v1/profile/me",
        json={"bio": "original bio", "city": "NYC"},
        headers=auth_user["headers"],
    )

    # Update only city
    resp = await client.put(
        "/api/v1/profile/me",
        json={"city": "LA"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["city"] == "LA"
    # bio should remain
    assert data["bio"] == "original bio"


@pytest.mark.asyncio
async def test_get_profile_by_user_id(client: AsyncClient, auth_user: Dict):
    """GET /profile/{user_id} returns the profile for another user."""
    # First create a profile for auth_user
    await client.put(
        "/api/v1/profile/me",
        json={"bio": "visible profile"},
        headers=auth_user["headers"],
    )

    user_id = auth_user["user"]["id"]
    resp = await client.get(
        f"/api/v1/profile/{user_id}", headers=auth_user["headers"]
    )
    assert resp.status_code == 200
    assert resp.json()["bio"] == "visible profile"


@pytest.mark.asyncio
async def test_get_profile_by_nonexistent_user_id(client: AsyncClient, auth_user: Dict):
    """GET /profile/{user_id} returns 404 for a UUID that has no profile."""
    fake_id = str(uuid.uuid4())
    resp = await client.get(
        f"/api/v1/profile/{fake_id}", headers=auth_user["headers"]
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_profile_unauthenticated(client: AsyncClient):
    """GET /profile/me without auth returns 401."""
    resp = await client.get("/api/v1/profile/me")
    assert resp.status_code == 401
