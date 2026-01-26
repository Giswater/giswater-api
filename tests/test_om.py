"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.helpers import skip_if_unhealthy


@pytest.mark.ws
def test_get_mincuts():
    client = TestClient(app)
    skip_if_unhealthy(client)

    response = client.get("/om/mincuts")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.ud
@pytest.mark.parametrize(
    ("initial_node_id", "final_node_id"),
    [
        (35, 38),
        (36, 37),
    ],
)
def test_create_profile(initial_node_id: int, final_node_id: int):
    client = TestClient(app)
    skip_if_unhealthy(client)

    payload = {
        "initial_node_id": initial_node_id,
        "final_node_id": final_node_id,
        "links_distance": 1,
        "scale_eh": 1000,
        "scale_ev": 1000,
    }

    response = client.post("/om/profiles", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data
