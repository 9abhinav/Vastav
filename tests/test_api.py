import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_settings_endpoints():
    # GET settings
    get_res = client.get("/api/settings")
    assert get_res.status_code == 200
    cfg = get_res.json()
    assert "speed_limit" in cfg

    # PUT settings
    cfg["speed_limit"] = 70.0
    put_res = client.put("/api/settings", json=cfg)
    assert put_res.status_code == 200
    assert put_res.json()["speed_limit"] == 70.0


def test_violations_flow():
    # Create violation
    payload = {
        "tracking_id": 99,
        "violation_type": "OVER_SPEEDING",
        "speed": 88.5,
        "speed_limit": 60.0,
        "plate_number": "TEST9999",
        "location": "Test Cam 01"
    }
    create_res = client.post("/api/violations", json=payload)
    assert create_res.status_code == 201
    v_data = create_res.json()
    v_id = v_data["id"]
    assert v_data["plate_number"] == "TEST9999"

    # Get single violation
    get_res = client.get(f"/api/violations/{v_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == v_id

    # List violations with filter
    list_res = client.get("/api/violations?plate_number=TEST9999")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # Update status
    update_res = client.put(f"/api/violations/{v_id}", json={"status": "CONFIRMED"})
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "CONFIRMED"


def test_statistics_endpoint():
    res = client.get("/api/statistics")
    assert res.status_code == 200
    data = res.json()
    assert "total_violations" in data
    assert "speed_distribution" in data
    assert "violations_by_type" in data
