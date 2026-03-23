"""Phase 2 tests: discovery, search, filters, facets."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
import pytest_asyncio
from httpx import AsyncClient

PROF_PAYLOAD = {
    "profile_type": "professional",
    "headline": "Python Backend Developer",
    "bio": "Building scalable APIs",
    "location": "San Francisco",
    "skills": ["python", "fastapi", "postgresql"],
    "professional_data": {
        "primary_role": "backend_developer",
        "years_experience": 8,
        "hourly_rate": 150.00,
        "availability_status": "available",
    },
}

ADVISOR_PAYLOAD = {
    "profile_type": "advisor",
    "headline": "Fintech Advisor",
    "bio": "Angel investor in fintech",
    "location": "New York",
    "skills": ["fundraising", "fintech"],
    "advisor_data": {
        "domain_expertise": ["fintech", "payments"],
        "investment_stages": ["seed", "pre_seed"],
        "fee_structure": "equity",
    },
}

FOUNDER_PAYLOAD = {
    "profile_type": "founder",
    "headline": "AI Startup Founder",
    "bio": "Building ML platform",
    "location": "Austin",
    "skills": ["machine-learning", "python"],
    "founder_data": {
        "looking_for_roles": ["cto", "designer"],
        "startup_stage": "pre_seed",
        "industry": "ai_ml",
        "commitment_level": "full_time",
    },
}


async def _create_and_publish(client: AsyncClient, headers: dict, payload: dict) -> dict:
    res = await client.post("/api/v1/marketplace/profiles", json=payload, headers=headers)
    assert res.status_code == 201, res.text
    await client.patch("/api/v1/marketplace/profiles/me/visibility", json={"is_public": True}, headers=headers)
    return res.json()


@pytest_asyncio.fixture
async def search_profiles(client: AsyncClient):
    """Create 3 different profile types, all published."""
    users = []
    for i, payload in enumerate([PROF_PAYLOAD, ADVISOR_PAYLOAD, FOUNDER_PAYLOAD]):
        email = f"search-test-{uuid.uuid4().hex[:6]}@example.com"
        reg = await client.post("/api/v1/auth/register", json={
            "email": email, "password": "Test1234!", "first_name": f"User{i}", "last_name": "Test",
        })
        assert reg.status_code == 201
        token = reg.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        profile = await _create_and_publish(client, headers, payload)
        users.append({"headers": headers, "profile": profile, "email": email})
    return users


class TestDiscover:

    async def test_discover_returns_public_profiles(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get("/api/v1/marketplace/discover", headers=auth_user["headers"])
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 3
        assert len(data["items"]) >= 3

    async def test_discover_filter_by_type(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover?profile_type=professional",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["profile_type"] == "professional"

    async def test_discover_filter_by_skills(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover?skills=python",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert "python" in item["skills"]

    async def test_discover_filter_by_location(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover?location=San Francisco",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert "San Francisco" in item["location"]

    async def test_discover_sort_by_newest(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover?sort_by=newest",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        assert resp.json()["total"] >= 3

    async def test_discover_with_facets(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover?include_facets=true",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["facets"] is not None
        assert "profile_types" in data["facets"]
        assert "skills" in data["facets"]
        assert "locations" in data["facets"]
        assert len(data["facets"]["profile_types"]) > 0


class TestDiscoverProfessionals:

    async def test_professionals_endpoint(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/professionals",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["profile_type"] == "professional"

    async def test_filter_by_availability(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/professionals?availability=available",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200

    async def test_filter_by_rate_range(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/professionals?min_rate=100&max_rate=200",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200

    async def test_filter_by_experience(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/professionals?min_experience=5",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200


class TestDiscoverAdvisors:

    async def test_advisors_endpoint(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/advisors",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["profile_type"] == "advisor"

    async def test_filter_by_expertise(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/advisors?domain_expertise=fintech",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200

    async def test_filter_by_fee_structure(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/advisors?fee_structure=equity",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200


class TestDiscoverFounders:

    async def test_founders_endpoint(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/founders",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        for item in resp.json()["items"]:
            assert item["profile_type"] == "founder"

    async def test_filter_by_industry(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/discover/founders?industry=ai_ml",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200


class TestUnifiedSearch:

    async def test_search_requires_query(self, client: AsyncClient, auth_user: Dict):
        resp = await client.get("/api/v1/marketplace/search", headers=auth_user["headers"])
        assert resp.status_code == 422  # q is required

    async def test_search_by_text(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/search?q=python",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] >= 1
        assert data["facets"] is not None

    async def test_search_returns_relevance_sorted(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/search?q=backend developer&sort_by=relevance",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200


class TestFacets:

    async def test_facets_endpoint(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/search/facets",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "profile_types" in data
        assert "skills" in data
        assert "availability" in data
        assert "hourly_rate_ranges" in data
        assert "locations" in data

    async def test_facets_with_type_filter(self, client: AsyncClient, search_profiles, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/search/facets?profile_type=professional",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["profile_types"]) >= 1
        # When filtering by professional, the type facet should include professional
        type_values = [pt["value"] for pt in data["profile_types"]]
        assert "professional" in type_values
