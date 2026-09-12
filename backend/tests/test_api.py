import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "The Lenny Growth Assistant" in data["app_name"]
    assert "version" in data


@pytest.mark.asyncio
async def test_diagnostics_endpoint(client: AsyncClient):
    response = await client.get("/api/diagnostics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "database_connected" in data
    assert "indexed_episodes" in data
    assert "indexed_chunks" in data
    assert data["indexed_episodes"] >= 1


@pytest.mark.asyncio
async def test_models_list_and_select(client: AsyncClient):
    response = await client.get("/api/models")
    assert response.status_code == 200
    data = response.json()
    assert "active_provider" in data
    assert len(data["models"]) >= 3

    # Switch provider
    sel_res = await client.post("/api/models/select", json={"provider": "anthropic"})
    assert sel_res.status_code == 200
    assert sel_res.json()["active_provider"] == "anthropic"


@pytest.mark.asyncio
async def test_sources_endpoints(client: AsyncClient):
    response = await client.get("/api/sources")
    assert response.status_code == 200
    sources = response.json()
    assert len(sources) >= 1
    assert any("Shreyas Doshi" in s["guest"] for s in sources)

    # Filter query
    filter_res = await client.get("/api/sources?query=Elena")
    assert filter_res.status_code == 200
    filtered = filter_res.json()
    assert len(filtered) >= 1
    assert "Elena Verna" in filtered[0]["guest"]
