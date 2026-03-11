"""Tests for /api/v1/auth — register, login, get me."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Registering a new user returns 201 with user object and access_token."""
    payload = {
        "email": f"reg-{uuid.uuid4().hex[:8]}@example.com",
        "password": "Str0ng!Pass",
        "first_name": "Jane",
        "last_name": "Doe",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == payload["email"]
    assert data["user"]["first_name"] == "Jane"
    assert data["user"]["last_name"] == "Doe"
    assert data["user"]["role"] == "founder"
    assert data["user"]["is_active"] is True
    assert "id" in data["user"]
    assert "created_at" in data["user"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Attempting to register with an existing email returns 400."""
    email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "Pass1234!",
        "first_name": "A",
        "last_name": "B",
    }
    resp1 = await client.post("/api/v1/auth/register", json=payload)
    assert resp1.status_code == 201

    resp2 = await client.post("/api/v1/auth/register", json=payload)
    assert resp2.status_code == 400
    assert "already registered" in resp2.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    """Missing required fields returns 422."""
    resp = await client.post("/api/v1/auth/register", json={"email": "x@y.com"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_invalid_email(client: AsyncClient):
    """Invalid email format returns 422."""
    payload = {
        "email": "not-an-email",
        "password": "Pass1234!",
        "first_name": "A",
        "last_name": "B",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, auth_user: Dict):
    """Logging in with valid credentials returns an access_token."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": auth_user["email"], "password": auth_user["password"]},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, auth_user: Dict):
    """Wrong password returns 401."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": auth_user["email"], "password": "WrongPassword!"},
    )
    assert resp.status_code == 401
    assert "invalid credentials" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_nonexistent_email(client: AsyncClient):
    """Unknown email returns 401."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@nowhere.com", "password": "x"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_user: Dict):
    """GET /me returns the authenticated user's data."""
    resp = await client.get("/api/v1/auth/me", headers=auth_user["headers"])
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == auth_user["user"]["id"]
    assert data["email"] == auth_user["email"]


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client: AsyncClient):
    """GET /me without a token returns 401."""
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_invalid_token(client: AsyncClient):
    """GET /me with an invalid token returns 401."""
    resp = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert resp.status_code == 401
