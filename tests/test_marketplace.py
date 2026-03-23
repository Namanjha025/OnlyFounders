"""Tests for the marketplace profile system (Phase 1)."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
import pytest_asyncio
from httpx import AsyncClient


# ── Helpers ────────────────────────────────────────────────────────

PROF_PAYLOAD = {
    "profile_type": "professional",
    "headline": "Senior Backend Developer",
    "bio": "10 years of experience building scalable systems",
    "location": "San Francisco, CA",
    "skills": ["python", "fastapi", "postgresql"],
    "linkedin_url": "https://linkedin.com/in/testdev",
    "professional_data": {
        "primary_role": "backend_developer",
        "years_experience": 10,
        "hourly_rate": 150.00,
        "availability_status": "available",
    },
}

ADVISOR_PAYLOAD = {
    "profile_type": "advisor",
    "headline": "Angel Investor & Startup Mentor",
    "bio": "Invested in 30+ startups",
    "skills": ["fundraising", "strategy"],
    "advisor_data": {
        "domain_expertise": ["fintech", "saas"],
        "investment_thesis": "Early-stage B2B SaaS",
        "fee_structure": "equity",
    },
}

FOUNDER_PAYLOAD = {
    "profile_type": "founder",
    "headline": "Technical Co-founder Seeking Business Partner",
    "bio": "Built 3 products from scratch",
    "skills": ["python", "react", "product"],
    "founder_data": {
        "looking_for_roles": ["cto", "designer"],
        "cofounder_brief": "Building an AI platform, need a business co-founder",
        "commitment_level": "full_time",
        "equity_offered": "20-30%",
    },
}


# ── Fixtures ───────────────────────────────────────────────────────

@pytest_asyncio.fixture
async def pro_profile(client: AsyncClient, auth_user: Dict) -> Dict:
    resp = await client.post(
        "/api/v1/marketplace/profiles",
        json=PROF_PAYLOAD,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


# ── Profile Creation ───────────────────────────────────────────────

class TestProfileCreation:

    async def test_create_professional_profile(self, client: AsyncClient, auth_user: Dict):
        resp = await client.post(
            "/api/v1/marketplace/profiles",
            json=PROF_PAYLOAD,
            headers=auth_user["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["profile_type"] == "professional"
        assert data["headline"] == "Senior Backend Developer"
        assert data["skills"] == ["python", "fastapi", "postgresql"]
        assert data["professional_data"] is not None
        assert data["professional_data"]["primary_role"] == "backend_developer"
        assert data["professional_data"]["years_experience"] == 10
        assert data["profile_score"] > 0

    async def test_create_advisor_profile(self, client: AsyncClient, auth_user: Dict):
        resp = await client.post(
            "/api/v1/marketplace/profiles",
            json=ADVISOR_PAYLOAD,
            headers=auth_user["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["profile_type"] == "advisor"
        assert data["advisor_data"] is not None
        assert data["advisor_data"]["domain_expertise"] == ["fintech", "saas"]

    async def test_create_founder_profile(self, client: AsyncClient, auth_user: Dict):
        resp = await client.post(
            "/api/v1/marketplace/profiles",
            json=FOUNDER_PAYLOAD,
            headers=auth_user["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["profile_type"] == "founder"
        assert data["founder_data"] is not None
        assert data["founder_data"]["looking_for_roles"] == ["cto", "designer"]

    async def test_create_duplicate_rejected(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.post(
            "/api/v1/marketplace/profiles",
            json=PROF_PAYLOAD,
            headers=auth_user["headers"],
        )
        assert resp.status_code == 409

    async def test_create_profile_unauthenticated(self, client: AsyncClient):
        resp = await client.post("/api/v1/marketplace/profiles", json=PROF_PAYLOAD)
        assert resp.status_code == 401

    async def test_create_profile_initial_score(self, client: AsyncClient, auth_user: Dict):
        resp = await client.post(
            "/api/v1/marketplace/profiles",
            json=PROF_PAYLOAD,
            headers=auth_user["headers"],
        )
        data = resp.json()
        # headline(8) + bio(8) + location(4) + skills(8) + linkedin(4) = 32 base
        # primary_role(10) + years_exp(8) + hourly_rate(5) + availability(8) = 31 type
        assert data["profile_score"] >= 50


# ── Profile Read ───────────────────────────────────────────────────

class TestProfileRead:

    async def test_get_my_profile(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.get(
            "/api/v1/marketplace/profiles/me",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == pro_profile["id"]
        assert data["headline"] == "Senior Backend Developer"
        assert "professional_data" in data
        assert "visibility_settings" in data  # Self view includes this

    async def test_get_my_profile_not_found(self, client: AsyncClient, auth_user: Dict):
        resp = await client.get(
            "/api/v1/marketplace/profiles/me",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 404

    async def test_get_profile_by_id_self_view(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.get(
            f"/api/v1/marketplace/profiles/{pro_profile['id']}",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        # Self view has visibility_settings
        assert "visibility_settings" in data

    async def test_get_public_profile_by_other_user(self, client: AsyncClient, auth_user: Dict, auth_user2: Dict, pro_profile: Dict):
        # First, make it public
        await client.patch(
            "/api/v1/marketplace/profiles/me/visibility",
            json={"is_public": True},
            headers=auth_user["headers"],
        )
        # Other user views it
        resp = await client.get(
            f"/api/v1/marketplace/profiles/{pro_profile['id']}",
            headers=auth_user2["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        # Public view — no visibility_settings
        assert "visibility_settings" not in data

    async def test_get_private_profile_hidden(self, client: AsyncClient, auth_user2: Dict, pro_profile: Dict):
        # Profile is private by default — other user should get 404
        resp = await client.get(
            f"/api/v1/marketplace/profiles/{pro_profile['id']}",
            headers=auth_user2["headers"],
        )
        assert resp.status_code == 404


# ── Profile Update ─────────────────────────────────────────────────

class TestProfileUpdate:

    async def test_update_base_fields(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.patch(
            "/api/v1/marketplace/profiles/me",
            json={"headline": "Updated Headline", "bio": "Updated bio"},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["headline"] == "Updated Headline"
        assert data["bio"] == "Updated bio"

    async def test_update_type_specific_fields(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.patch(
            "/api/v1/marketplace/profiles/me/type-data",
            json={"professional_data": {"primary_role": "fullstack_developer", "years_experience": 12}},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["professional_data"]["primary_role"] == "fullstack_developer"
        assert data["professional_data"]["years_experience"] == 12

    async def test_update_recalculates_score(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        old_score = pro_profile["profile_score"]
        # Add website_url which wasn't in original payload
        resp = await client.patch(
            "/api/v1/marketplace/profiles/me",
            json={"website_url": "https://example.com"},
            headers=auth_user["headers"],
        )
        data = resp.json()
        assert data["profile_score"] >= old_score


# ── Profile Delete ─────────────────────────────────────────────────

class TestProfileDelete:

    async def test_delete_own_profile(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.delete(
            "/api/v1/marketplace/profiles/me",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 204

        # Verify it's gone
        resp = await client.get(
            "/api/v1/marketplace/profiles/me",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 404

    async def test_delete_unauthenticated(self, client: AsyncClient):
        resp = await client.delete("/api/v1/marketplace/profiles/me")
        assert resp.status_code == 401


# ── Onboarding ─────────────────────────────────────────────────────

class TestOnboarding:

    async def test_start_onboarding(self, client: AsyncClient, auth_user: Dict):
        resp = await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "professional"},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["profile_type"] == "professional"
        assert data["completed_steps"] == []
        assert data["total_steps"] == 4
        assert data["is_complete"] is False

    async def test_save_step(self, client: AsyncClient, auth_user: Dict):
        # Start onboarding
        await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "professional"},
            headers=auth_user["headers"],
        )

        # Save step 1
        resp = await client.patch(
            "/api/v1/marketplace/onboarding/step/1",
            json={"data": {"headline": "Test Dev", "bio": "Hello", "location": "NYC"}},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert 1 in data["completed_steps"]
        assert data["profile_score"] > 0

    async def test_complete_flow(self, client: AsyncClient, auth_user: Dict):
        await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "professional"},
            headers=auth_user["headers"],
        )

        for step in range(1, 5):
            step_data = {}
            if step == 1:
                step_data = {"headline": "Dev", "bio": "Bio", "location": "NYC"}
            elif step == 2:
                step_data = {"skills": ["python"], "primary_role": "backend", "years_experience": 5}
            elif step == 3:
                step_data = {"hourly_rate": 100, "availability_status": "available"}
            elif step == 4:
                step_data = {"linkedin_url": "https://linkedin.com/in/test"}

            resp = await client.patch(
                f"/api/v1/marketplace/onboarding/step/{step}",
                json={"data": step_data},
                headers=auth_user["headers"],
            )
            assert resp.status_code == 200

        data = resp.json()
        assert data["is_complete"] is True
        assert len(data["completed_steps"]) == 4

    async def test_invalid_step(self, client: AsyncClient, auth_user: Dict):
        await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "professional"},
            headers=auth_user["headers"],
        )
        resp = await client.patch(
            "/api/v1/marketplace/onboarding/step/5",
            json={"data": {"headline": "Test"}},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 400

    async def test_get_status(self, client: AsyncClient, auth_user: Dict):
        await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "advisor"},
            headers=auth_user["headers"],
        )
        resp = await client.get(
            "/api/v1/marketplace/onboarding/status",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["profile_type"] == "advisor"

    async def test_duplicate_start_rejected(self, client: AsyncClient, auth_user: Dict):
        await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "professional"},
            headers=auth_user["headers"],
        )
        resp = await client.post(
            "/api/v1/marketplace/onboarding/start",
            json={"profile_type": "advisor"},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 409


# ── Visibility ─────────────────────────────────────────────────────

class TestVisibility:

    async def test_get_visibility_settings(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.get(
            "/api/v1/marketplace/profiles/me/visibility",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_public"] is False
        assert "show_email" in data

    async def test_publish_profile(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.patch(
            "/api/v1/marketplace/profiles/me/visibility",
            json={"is_public": True},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_public"] is True

    async def test_update_visibility_settings(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.patch(
            "/api/v1/marketplace/profiles/me/visibility",
            json={"show_email": True, "show_phone": True},
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["show_email"] is True
        assert data["show_phone"] is True


# ── Documents ──────────────────────────────────────────────────────

class TestDocuments:

    async def test_list_documents_empty(self, client: AsyncClient, auth_user: Dict, pro_profile: Dict):
        resp = await client.get(
            "/api/v1/marketplace/profiles/me/documents",
            headers=auth_user["headers"],
        )
        assert resp.status_code == 200
        assert resp.json() == []
