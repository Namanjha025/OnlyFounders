"""Tests for /api/v1/startups/{startup_id}/calendar — CRUD, date/type filters."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_events_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /calendar/ returns an empty list initially."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_event(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /calendar/ creates a calendar event."""
    payload = {
        "title": "Board Meeting",
        "description": "Quarterly board review",
        "event_type": "meeting",
        "event_date": "2025-07-15",
        "event_time": "14:00:00",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Board Meeting"
    assert data["event_type"] == "meeting"
    assert data["event_date"] == "2025-07-15"
    assert data["startup_id"] == test_startup["id"]
    assert data["created_by_user"] == auth_user["user"]["id"]


@pytest.mark.asyncio
async def test_create_event_missing_required_fields(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /calendar/ without required fields returns 422."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={"title": "No event_type or event_date"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_update_event(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /calendar/{event_id} updates the event."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={
            "title": "Old Title",
            "event_type": "reminder",
            "event_date": "2025-08-01",
        },
        headers=auth_user["headers"],
    )
    event_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/calendar/{event_id}",
        json={"title": "New Title", "event_date": "2025-08-02"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "New Title"
    assert resp.json()["event_date"] == "2025-08-02"


@pytest.mark.asyncio
async def test_update_event_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /calendar/{bad_id} returns 404."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/calendar/{uuid.uuid4()}",
        json={"title": "Ghost"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_event(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /calendar/{event_id} removes the event."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={
            "title": "To Delete",
            "event_type": "deadline",
            "event_date": "2025-12-31",
        },
        headers=auth_user["headers"],
    )
    event_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/calendar/{event_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_event_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /calendar/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/calendar/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_events_filter_by_type(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /calendar/?type=meeting filters by event type."""
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={
            "title": "Meeting A",
            "event_type": "meeting",
            "event_date": "2025-09-01",
        },
        headers=auth_user["headers"],
    )
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={
            "title": "Milestone A",
            "event_type": "milestone",
            "event_date": "2025-09-02",
        },
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        params={"type": "meeting"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    for e in resp.json():
        assert e["event_type"] == "meeting"


@pytest.mark.asyncio
async def test_list_events_filter_by_date_range(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /calendar/?from_date=...&to_date=... filters by date range."""
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={
            "title": "Early Event",
            "event_type": "reminder",
            "event_date": "2025-01-01",
        },
        headers=auth_user["headers"],
    )
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        json={
            "title": "Late Event",
            "event_type": "reminder",
            "event_date": "2025-12-31",
        },
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        params={"from_date": "2025-06-01", "to_date": "2025-06-30"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    for e in resp.json():
        assert "2025-06-01" <= e["event_date"] <= "2025-06-30"


@pytest.mark.asyncio
async def test_calendar_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/calendar/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_calendar_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot access calendar events."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/calendar/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
