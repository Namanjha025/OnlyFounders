"""Tests for /api/v1/startups/{startup_id}/documents — list, upload-url, confirm, download, delete.

S3 operations are mocked so tests run without AWS credentials.
"""
from __future__ import annotations

import uuid
from typing import Dict
from unittest.mock import patch

import pytest
from httpx import AsyncClient


MOCK_UPLOAD_URL = "https://s3.amazonaws.com/bucket/presigned-upload"
MOCK_S3_KEY = "startups/fake/documents/fake-key.pdf"
MOCK_DOWNLOAD_URL = "https://s3.amazonaws.com/bucket/presigned-download"


def _mock_generate_upload(*args, **kwargs):
    return {"upload_url": MOCK_UPLOAD_URL, "s3_key": MOCK_S3_KEY}


def _mock_generate_download(*args, **kwargs):
    return MOCK_DOWNLOAD_URL


def _mock_delete_s3(*args, **kwargs):
    return None


@pytest.mark.asyncio
async def test_list_documents_empty(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/ returns an empty list initially."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/documents/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
@patch("app.routers.documents.generate_upload_presigned_url", _mock_generate_upload)
async def test_get_upload_url(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /documents/upload-url returns a presigned URL and s3_key."""
    payload = {
        "file_name": "pitch.pdf",
        "category": "pitch_deck",
        "mime_type": "application/pdf",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/upload-url",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["upload_url"] == MOCK_UPLOAD_URL
    assert data["s3_key"] == MOCK_S3_KEY


@pytest.mark.asyncio
async def test_confirm_upload(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """POST /documents/confirm-upload creates a Document record."""
    payload = {
        "s3_key": "startups/test/docs/confirmed.pdf",
        "name": "Pitch Deck Q4",
        "category": "pitch_deck",
        "file_name": "pitch.pdf",
        "file_size": 1024000,
        "mime_type": "application/pdf",
    }
    resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/confirm-upload",
        json=payload,
        headers=auth_user["headers"],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Pitch Deck Q4"
    assert data["category"] == "pitch_deck"
    assert data["file_size"] == 1024000
    assert data["startup_id"] == test_startup["id"]
    assert data["uploaded_by"] == auth_user["user"]["id"]


@pytest.mark.asyncio
async def test_list_documents_after_upload(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """After confirming an upload, GET /documents/ includes the document."""
    # Confirm an upload first
    await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/confirm-upload",
        json={
            "s3_key": "startups/test/docs/listed.pdf",
            "name": "Listed Doc",
            "category": "other",
            "file_name": "listed.pdf",
            "file_size": 512,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/documents/",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    names = [d["name"] for d in resp.json()]
    assert "Listed Doc" in names


@pytest.mark.asyncio
@patch("app.routers.documents.generate_download_presigned_url", _mock_generate_download)
async def test_get_download_url(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/{doc_id}/download-url returns a presigned download URL."""
    # Create a doc
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/confirm-upload",
        json={
            "s3_key": "startups/test/docs/download.pdf",
            "name": "Download Me",
            "category": "financials",
            "file_name": "download.pdf",
            "file_size": 256,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )
    doc_id = create_resp.json()["id"]

    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/documents/{doc_id}/download-url",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 200
    assert resp.json()["download_url"] == MOCK_DOWNLOAD_URL


@pytest.mark.asyncio
async def test_download_url_doc_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """GET /documents/{bad_id}/download-url returns 404."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/documents/{uuid.uuid4()}/download-url",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
@patch("app.routers.documents.delete_s3_object", _mock_delete_s3)
async def test_delete_document(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /documents/{doc_id} removes the document."""
    create_resp = await client.post(
        f"/api/v1/startups/{test_startup['id']}/documents/confirm-upload",
        json={
            "s3_key": "startups/test/docs/todelete.pdf",
            "name": "Delete Me",
            "category": "other",
            "file_name": "todelete.pdf",
            "file_size": 100,
            "mime_type": "application/pdf",
        },
        headers=auth_user["headers"],
    )
    doc_id = create_resp.json()["id"]

    del_resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/documents/{doc_id}",
        headers=auth_user["headers"],
    )
    assert del_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_document_not_found(
    client: AsyncClient, auth_user: Dict, test_startup: Dict
):
    """DELETE /documents/{bad_id} returns 404."""
    resp = await client.delete(
        f"/api/v1/startups/{test_startup['id']}/documents/{uuid.uuid4()}",
        headers=auth_user["headers"],
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_documents_unauthenticated(client: AsyncClient, test_startup: Dict):
    """Unauthenticated requests to documents return 401."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/documents/"
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_documents_forbidden_non_member(
    client: AsyncClient, auth_user2: Dict, test_startup: Dict
):
    """Non-member cannot list documents."""
    resp = await client.get(
        f"/api/v1/startups/{test_startup['id']}/documents/",
        headers=auth_user2["headers"],
    )
    assert resp.status_code == 403
