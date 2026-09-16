"""Tests for investigate API endpoints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from db_copilot.api.app import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


class TestInvestigateAPI:
    @pytest.mark.asyncio
    async def test_submit_investigation_returns_202(self, client):
        resp = await client.post(
            "/api/v1/investigate",
            json={"question": "Why is the database slow?", "database_name": "ORCL"},
        )
        assert resp.status_code == 202
        data = resp.json()
        assert "id" in data
        assert data["status"] == "queued"

    @pytest.mark.asyncio
    async def test_get_investigation_queued_state(self, client):
        # Submit first
        submit = await client.post(
            "/api/v1/investigate",
            json={"question": "Test question"},
        )
        inv_id = submit.json()["id"]

        # Poll
        resp = await client.get(f"/api/v1/investigate/{inv_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == inv_id
        assert data["status"] in ("queued", "running", "completed", "partial", "failed")

    @pytest.mark.asyncio
    async def test_get_nonexistent_investigation_returns_404(self, client):
        resp = await client.get("/api/v1/investigate/00000000-0000-0000-0000-000000000000")
        assert resp.status_code == 404
