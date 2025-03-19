from fastapi.testclient import TestClient
from ..app.main import app

client = TestClient(app)

def test_get_status():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
