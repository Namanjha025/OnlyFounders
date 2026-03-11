"""Tests for /api/v1/startups/{startup_id}/onboarding — progress computation."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_onboarding_initial_state(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /onboarding/ returns section statuses with low completeness for a fresh startup."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "overall_completeness" in data
    assert "sections" in data
    sections = data["sections"]

    # Expected sections
    expected_sections = [
        "founder_profile",
        "company_basics",
        "team",
        "product",
        "traction",
        "financials",
        "documents",
    ]
    for section in expected_sections:
        assert section in sections
        assert "complete" in sections[section]
        assert "completeness" in sections[section]


@pytest.mark.asyncio
async def test_onboarding_team_section(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Team completeness should be >= 50 with at least the founder member (auto-created)."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    data = resp.json()
    team = data["sections"]["team"]
    # At least 1 member (founder); manager agent may also be present
    assert team["completeness"] >= 50
    assert team["complete"] is True


@pytest.mark.asyncio
async def test_onboarding_team_section_with_two_members(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Team completeness should be 100 with 2+ members."""
    # Add another member
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/",
        json={"name": "Second Member", "role": "cto"},
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    data = resp.json()
    assert data["sections"]["team"]["completeness"] == 100
    assert data["sections"]["team"]["complete"] is True


@pytest.mark.asyncio
async def test_onboarding_product_section_after_upsert(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Product completeness increases after filling fields."""
    # Initially product is 0%
    resp1 = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    assert resp1.json()["sections"]["product"]["completeness"] == 0

    # Fill all 7 tracked product fields
    await client.put(
        f"/api/v1/startups/{test_startup['id']}/product/",
        json={
            "problem": "X",
            "solution": "Y",
            "product_stage": "mvp",
            "target_audience": "SMBs",
            "tam": 1000000,
            "competitive_advantage": "Speed",
            "revenue_model": "SaaS",
        },
        headers=auth_user["headers"],
    )

    resp2 = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    assert resp2.json()["sections"]["product"]["completeness"] == 100
    assert resp2.json()["sections"]["product"]["complete"] is True


@pytest.mark.asyncio
async def test_onboarding_documents_section(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Documents completeness increases with uploaded documents."""
    # Initially 0
    resp1 = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    assert resp1.json()["sections"]["documents"]["completeness"] == 0

    # Upload one doc
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/confirm-upload",
        json={
            "s3_key": "test/onboarding/doc1.pdf",
            "name": "Doc 1",
            "category": "pitch_deck",
            "file_name": "doc1.pdf",
            "file_size": 100,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )

    resp2 = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    assert resp2.json()["sections"]["documents"]["completeness"] == 50

    # Upload second doc
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/confirm-upload",
        json={
            "s3_key": "test/onboarding/doc2.pdf",
            "name": "Doc 2",
            "category": "financials",
            "file_name": "doc2.pdf",
            "file_size": 200,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )

    resp3 = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    assert resp3.json()["sections"]["documents"]["completeness"] == 100


@pytest.mark.asyncio
async def test_onboarding_overall_completeness(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Overall completeness is the average of all section completeness values."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    data = resp.json()
    sections = data["sections"]
    expected_overall = int(
        sum(s["completeness"] for s in sections.values()) / len(sections)
    )
    assert data["overall_completeness"] == expected_overall


@pytest.mark.asyncio
async def test_onboarding_founder_profile_section(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Founder profile completeness reflects filled profile fields."""
    # Fill some founder profile fields
    await client.put(
        "/api/v1/profile/me",
        json={
            "phone": "+1234567890",
            "bio": "Test bio",
            "linkedin_url": "https://linkedin.com/in/test",
            "city": "NYC",
            "country": "US",
            "is_technical": True,
            "is_full_time": True,
            "education": "MIT",
            "years_of_experience": 5,
            "notable_achievement": "Built a unicorn",
            "skills": ["python"],
        },
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user["headers"],
    )
    data = resp.json()
    fp = data["sections"]["founder_profile"]
    # All 11 fields filled -> 100%
    assert fp["completeness"] == 100
    assert fp["complete"] is True


@pytest.mark.asyncio
async def test_onboarding_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_onboarding_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot access onboarding status."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/onboarding/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
