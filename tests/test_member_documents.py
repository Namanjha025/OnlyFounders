"""Tests for /api/v1/startups/{sid}/members/{mid}/documents — member-scoped document CRUD.

S3 operations are mocked.
"""
from __future__ import annotations

import uuid
from typing import Dict
from unittest.mock import patch

import pytest
from httpx import AsyncClient


MOCK_UPLOAD_URL = "https://s3.amazonaws.com/bucket/member-upload"
MOCK_S3_KEY = "startups/fake/documents/member-key.pdf"
MOCK_DOWNLOAD_URL = "https://s3.amazonaws.com/bucket/member-download"


def _mock_generate_upload(*args, **kwargs):
    return {"upload_url": MOCK_UPLOAD_URL, "s3_key": MOCK_S3_KEY}


def _mock_generate_download(*args, **kwargs):
    return MOCK_DOWNLOAD_URL


def _mock_delete_s3(*args, **kwargs):
    return None


async def _get_founder_member_id(
    client: AsyncClient, startup_id: str, headers: Dict
) -> str:
    """Helper: fetch the auto-created founder member id."""
    resp = await client.get(
        f"/api/v1/startups/{startup_id}/members/", headers=headers
    )
    members = resp.json()
    for m in members:
        if m["role"] == "founder":
            return m["id"]
    raise AssertionError("No founder member found")


@pytest.mark.asyncio
async def test_list_member_documents_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/ returns an empty list for a member with no documents."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_member_documents_member_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/ for a nonexistent member returns 404."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/{uuid.uuid4()}/documents/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.routers.member_documents.generate_upload_presigned_url", _mock_generate_upload)
async def test_get_member_doc_upload_url(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /documents/upload-url returns a presigned URL."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    payload = {
        "file_name": "contract.pdf",
        "category": "contract",
        "mime_type": "application/pdf",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/upload-url",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["upload_url"] == MOCK_UPLOAD_URL
    assert data["s3_key"] == MOCK_S3_KEY


@pytest.mark.asyncio
async def test_confirm_member_doc_upload(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /documents/confirm-upload creates a MemberDocument record."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    payload = {
        "s3_key": "startups/test/member/confirmed.pdf",
        "name": "Offer Letter",
        "category": "offer_letter",
        "file_name": "offer.pdf",
        "file_size": 2048,
        "mime_type": "application/pdf",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/confirm-upload",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Offer Letter"
    assert data["category"] == "offer_letter"
    assert data["member_id"] == member_id
    assert data["startup_id"] == test_startup["id"]


@pytest.mark.asyncio
async def test_list_member_documents_after_upload(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """After confirming, the document appears in the list."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/confirm-upload",
        json={
            "s3_key": "startups/test/member/listed.pdf",
            "name": "Listed MemberDoc",
            "category": "nda",
            "file_name": "nda.pdf",
            "file_size": 256,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    names = [d["name"] for d in resp.json()]
    assert "Listed MemberDoc" in names


@pytest.mark.asyncio
@patch(
    "app.routers.member_documents.generate_download_presigned_url", _mock_generate_download
)
async def test_get_member_doc_download_url(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/{doc_id}/download-url returns a download URL."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/confirm-upload",
        json={
            "s3_key": "startups/test/member/download.pdf",
            "name": "Download MemberDoc",
            "category": "tax_form",
            "file_name": "tax.pdf",
            "file_size": 512,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )
    doc_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/{doc_id}/download-url",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["download_url"] == MOCK_DOWNLOAD_URL


@pytest.mark.asyncio
async def test_download_member_doc_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/{bad_id}/download-url returns 404."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/{uuid.uuid4()}/download-url",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.routers.member_documents.delete_s3_object", _mock_delete_s3)
async def test_delete_member_document(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /documents/{doc_id} removes the member document."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/confirm-upload",
        json={
            "s3_key": "startups/test/member/todelete.pdf",
            "name": "To Delete",
            "category": "other",
            "file_name": "del.pdf",
            "file_size": 64,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )
    doc_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/{doc_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_member_document_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /documents/{bad_id} returns 404."""
    member_id = await _get_founder_member_id(
        client, test_startup["id"], auth_user["headers"]
    )
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/members/{member_id}/documents/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_member_documents_unauthenticated(
    client: AsyncClient, test_startup: Dict
):
    """Unauthenticated requests return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/members/{uuid.uuid4()}/documents/"
    )
    assert resp.status_code == 401
