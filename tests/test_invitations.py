"""Tests for invitation endpoints — send, list, accept, decline."""
from __future__ import annotations

import uuid
from typing import Dict

import pytest
from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Send invitation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_send_invitation(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Owner can send an invitation to another platform user."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "cto",
            "title": "CTO",
            "responsibilities": "Lead engineering",
            "message": "Join us!",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["status"] == "pending"
    assert data["invited_user_id"] == auth_user2["user"]["id"]
    assert data["role"] == "cto"
    assert data["title"] == "CTO"
    assert data["message"] == "Join us!"


@pytest.mark.asyncio
async def test_send_invitation_cannot_invite_self(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Cannot invite yourself."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user["user"]["id"],
            "role": "advisor",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 400
    assert "Cannot invite yourself" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_send_invitation_user_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """Inviting a non-existent user returns 404."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": str(uuid.uuid4()),
            "role": "employee",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_invitation_non_owner_forbidden(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Non-owner cannot send invitations."""
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user["user"]["id"],
            "role": "employee",
        },
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# List invitations (startup owner view)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_startup_invitations(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Owner can list all invitations for the startup."""
    # Send an invite first
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "advisor",
        },
        headers=auth_user["headers"],
    )

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    invites = resp.json()
    assert isinstance(invites, list)
    assert len(invites) >= 1


# ---------------------------------------------------------------------------
# List my invitations (invited user view)
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_list_my_invitations(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Invited user can see their pending invitations."""
    # Send invite
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "employee",
        },
        headers=auth_user["headers"],
    )

    resp = await client.get(
        "/api/v1/me/invitations",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 200
    invites = resp.json()
    assert isinstance(invites, list)
    assert len(invites) >= 1
    assert all(i["status"] == "pending" for i in invites)


# ---------------------------------------------------------------------------
# Accept invitation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_accept_invitation(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Accepting creates a startup_member record."""
    # Send invite
    send_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "cto",
            "title": "Chief Tech Officer",
            "responsibilities": "Build the product",
        },
        headers=auth_user["headers"],
    )
    invite_id = send_resp.json()["id"]

    # Accept
    resp = await client.put(
        f"/api/v1/invitations/{invite_id}/accept",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 200, resp.text
    data = resp.json()
    assert data["status"] == "accepted"
    assert data["responded_at"] is not None

    # Verify team member was created
    members_resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/",
        headers=auth_user["headers"],
    )
    members = members_resp.json()
    user2_members = [m for m in members if m.get("user_id") == auth_user2["user"]["id"]]
    assert len(user2_members) == 1
    assert user2_members[0]["role"] == "cto"
    assert user2_members[0]["title"] == "Chief Tech Officer"


# ---------------------------------------------------------------------------
# Decline invitation
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_decline_invitation(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Declining updates status but does not create a member."""
    # Send invite
    send_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "advisor",
        },
        headers=auth_user["headers"],
    )
    invite_id = send_resp.json()["id"]

    # Decline
    resp = await client.put(
        f"/api/v1/invitations/{invite_id}/decline",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "declined"
    assert data["responded_at"] is not None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_cannot_accept_someone_elses_invitation(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """A user cannot accept an invitation meant for someone else."""
    send_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "employee",
        },
        headers=auth_user["headers"],
    )
    invite_id = send_resp.json()["id"]

    # auth_user (the owner, not the invitee) tries to accept
    resp = await client.put(
        f"/api/v1/invitations/{invite_id}/accept",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_cannot_accept_already_accepted(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Cannot accept an invitation that's already been accepted."""
    send_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "cofounder",
        },
        headers=auth_user["headers"],
    )
    invite_id = send_resp.json()["id"]

    # Accept once
    await client.put(
        f"/api/v1/invitations/{invite_id}/accept",
        headers=auth_user2["headers"],
    )

    # Try to accept again
    resp = await client.put(
        f"/api/v1/invitations/{invite_id}/accept",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 400
    assert "already accepted" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_invitation_not_found(
    client: AsyncClient, auth_user: Dict
):
    """Accepting a non-existent invitation returns 404."""
    resp = await client.put(
        f"/api/v1/invitations/{uuid.uuid4()}/accept",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_pending_invite_blocked(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Cannot send a second pending invite to the same user for the same startup."""
    payload = {
        "invited_user_id": auth_user2["user"]["id"],
        "role": "employee",
    }

    # First invite
    resp1 = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp1.status_code == 201

    # Duplicate
    resp2 = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp2.status_code == 409


@pytest.mark.asyncio
async def test_already_member_blocked(
    client: AsyncClient, auth_user: Dict, auth_user2: Dict, test_startup: Dict
):
    """Cannot invite a user who is already a team member."""
    # Send and accept invite to make them a member
    send_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "employee",
        },
        headers=auth_user["headers"],
    )
    invite_id = send_resp.json()["id"]
    await client.put(
        f"/api/v1/invitations/{invite_id}/accept",
        headers=auth_user2["headers"],
    )

    # Try to invite again
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/invitations/",
        json={
            "invited_user_id": auth_user2["user"]["id"],
            "role": "advisor",
        },
        headers=auth_user["headers"],
    )
    assert resp.status_code == 409
    assert "already a team member" in resp.json()["detail"]
