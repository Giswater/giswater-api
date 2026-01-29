"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import pytest

from tests.helpers import assert_healthy


@pytest.mark.ws
@pytest.mark.skip(reason="Database function refactor in progress")
def test_get_mincuts(client, default_params):
    assert_healthy(client)

    response = client.get("/om/mincuts", params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"
    assert "body" in data


@pytest.mark.ud
@pytest.mark.parametrize(
    ("initial_node_id", "final_node_id", "expected_status", "expected_api_status"),
    [
        (35, 38, 200, "Accepted"),
        (36, 37, 500, "Failed"),
    ],
)
def test_create_profile(
    client, default_params, initial_node_id: int, final_node_id: int, expected_status: int, expected_api_status: str
):
    assert_healthy(client)

    payload = {
        "initial_node_id": initial_node_id,
        "final_node_id": final_node_id,
        "links_distance": 1,
        "scale_eh": 1000,
        "scale_ev": 1000,
    }

    response = client.post("/om/profiles", params=default_params, json=payload)

    assert response.status_code == expected_status
    data = response.json()
    assert data["status"] == expected_api_status
    if expected_status == 200:
        assert "body" in data
