"""Tests for /api/v1/startups/{startup_id}/tasks — CRUD, status/assigned_to filters, completed_at."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_tasks_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /tasks/ returns an empty list initially."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_task(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /tasks/ creates a task."""
    payload = {
        "title": "Build MVP",
        "description": "Ship the first version",
        "status": "pending",
        "priority": "high",
        "due_date": "2025-06-01",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Build MVP"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["startup_id"] == test_startup["id"]
    assert data["completed_at"] is None


@pytest.mark.asyncio
async def test_create_task_missing_title(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /tasks/ without required 'title' returns 422."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"description": "No title"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_task(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /tasks/{task_id} returns the task."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "Specific Task"},
        headers=auth_user["headers"],
    )
    task_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/{task_id}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /tasks/{bad_id} returns 404."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_task(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /tasks/{task_id} updates the task."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "To Update"},
        headers=auth_user["headers"],
    )
    task_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/tasks/{task_id}",
        json={"title": "Updated Title", "priority": "urgent"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Title"
    assert resp.json()["priority"] == "urgent"


@pytest.mark.asyncio
async def test_update_task_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """PUT /tasks/{bad_id} returns 404."""
    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/tasks/{uuid.uuid4()}",
        json={"title": "Ghost"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_task_completed_sets_completed_at(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Setting status to 'completed' auto-fills completed_at."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "Will Complete"},
        headers=auth_user["headers"],
    )
    task_id = create_resp.json()["id"]
    assert create_resp.json()["completed_at"] is None

    resp = await client.put(
        f"/api/v1/startups/{test_startup['id']}/tasks/{task_id}",
        json={"status": "completed"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert resp.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_delete_task(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /tasks/{task_id} removes the task."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "To Delete"},
        headers=auth_user["headers"],
    )
    task_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/tasks/{task_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204

    # Verify it is gone
    get_resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/{task_id}",
        headers=auth_user["headers"],
    )
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /tasks/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/tasks/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks_filter_by_status(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /tasks/?status=pending filters by status."""
    # Create a pending task and a completed task
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "Pending One", "status": "pending"},
        headers=auth_user["headers"],
    )
    cr = await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "In Progress One", "status": "in_progress"},
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        params={"status": "in_progress"},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    tasks = resp.json()
    for t in tasks:
        assert t["status"] == "in_progress"


@pytest.mark.asyncio
async def test_list_tasks_filter_by_assigned_to(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /tasks/?assigned_to={member_id} filters by assignee."""
    # Get a member id
    members_resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/",
        headers=auth_user["headers"],
    )
    member_id = members_resp.json()[0]["id"]

    # Create tasks with different assignees
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "Assigned Task", "assigned_to": member_id},
        headers=auth_user["headers"],
    )
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        json={"title": "Unassigned Task"},
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        params={"assigned_to": member_id},
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    tasks = resp.json()
    for t in tasks:
        assert t["assigned_to"] == member_id


@pytest.mark.asyncio
async def test_tasks_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tasks_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot access tasks."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/tasks/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
