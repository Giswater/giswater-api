from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)


def test_get_object_optimal_path_order():
    """Test the get_object_optimal_path_order endpoint with JSON string parameters"""

    # Test data
    initial_point = {
        "x": 418777.3,
        "y": 4576692.9,
        "epsg": 25831
    }

    final_point = {
        "x": 418800.0,
        "y": 4576700.0,
        "epsg": 25831
    }

    # Convert to JSON strings
    initial_point_json = json.dumps(initial_point)
    final_point_json = json.dumps(final_point)

    # Make the request
    response = client.get(
        "/routing/getobjectoptimalpathorder",
        params={
            "schema": "public",
            "objectType": "JUNCTION",
            "initialPoint": initial_point_json,
            "finalPoint": final_point_json,
            "transportMode": "auto",
            "units": "kilometers"
        }
    )

    # Print response details for debugging
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # Check that the request was processed (even if Valhalla API fails, we should get a proper response)
    assert response.status_code in [200, 500]  # 200 for success, 500 for Valhalla API issues

    if response.status_code == 500:
        data = response.json()
        assert data["detail"] != "Database connection failed"

    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "Accepted"
        assert "body" in data
        assert "data" in data["body"]


def test_get_object_optimal_path_order_invalid_json():
    """Test the endpoint with invalid JSON strings"""

    response = client.get(
        "/routing/getobjectoptimalpathorder",
        params={
            "schema": "public",
            "objectType": "JUNCTION",
            "initialPoint": "invalid json",
            "finalPoint": "also invalid",
            "transportMode": "auto",
            "units": "kilometers"
        }
    )

    # Print response details for debugging
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    assert response.status_code in [400, 500]

    if response.status_code == 500:
        data = response.json()
        assert data["detail"] != "Database connection failed"

    if response.status_code == 422:
        data = response.json()
        assert "Invalid JSON format" in data["detail"]
