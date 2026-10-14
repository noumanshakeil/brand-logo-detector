import pytest

@pytest.mark.asyncio
async def test_match_confidence(client):
    await client.post("/api/brands", json={"name": "Acme", "aliases": ["acme corp"]})
    j = await client.post("/api/jobs", json={"asset_name": "ad.png", "hint_text": "Acme corp logo in corner"})
    jid = j.json()["id"]
    await client.post(f"/api/jobs/{jid}/run")
    m = await client.get(f"/api/jobs/{jid}/matches")
    assert m.status_code == 200
    assert m.json()["matches"][0]["confidence"] > 0.3
