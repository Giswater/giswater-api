"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import pytest
from uuid import uuid4

from tests.helpers import assert_ready, api


DSCENARIO_OBJECT_TYPES = [
    "connec",
    "controls",
    "demand",
    "frpump",
    "frshortpipe",
    "frvalve",
    "inlet",
    "junction",
    "pipe",
    "pump",
    "pump_additional",
    "reservoir",
    "rules",
    "shortpipe",
    "tank",
    "valve",
    "virtualpump",
    "virtualvalve",
]


def _new_dscenario_name() -> str:
    return f"TEST_DS_{uuid4().hex[:10]}"


def _create_dscenario(client, default_params) -> int:
    payload = {
        "name": _new_dscenario_name(),
        "descript": "test dscenario",
        "parent": None,
        "type": "DEMAND",
        "active": True,
        "expl": 0,
    }
    response = client.post(api("/epa/dscenarios"), params=default_params, json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "Accepted"

    dscenario_id = data["body"]["data"]["dscenario_id"]
    return dscenario_id


@pytest.mark.ws
@pytest.mark.parametrize("object_type", DSCENARIO_OBJECT_TYPES)
def test_get_dscenario_objects(client, default_params, object_type: str):
    """Smoke test for list endpoint for each dscenario object type."""
    assert_ready(client)

    # Use a generic dscenario_id; database contents will determine whether it's non-empty.
    response = client.get(api(f"/epa/dscenarios/1/{object_type}"), params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "body" in data


@pytest.mark.ws
@pytest.mark.parametrize("object_type", DSCENARIO_OBJECT_TYPES)
def test_get_dscenario_object_not_found(client, default_params, object_type: str):
    """GET single object should return 404 for non-existing ids."""
    assert_ready(client)

    response = client.get(api(f"/epa/dscenarios/999999/{object_type}/999999"), params=default_params)

    assert response.status_code == 404
    assert response.json()["detail"] == "Object not found"


@pytest.mark.ws
@pytest.mark.parametrize("object_type", DSCENARIO_OBJECT_TYPES)
def test_delete_dscenario_object_not_found(client, default_params, object_type: str):
    """DELETE single object should return 404 for non-existing ids."""
    assert_ready(client)

    response = client.delete(
        api(f"/epa/dscenarios/999999/{object_type}/999999"),
        params=default_params,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Object not found"


@pytest.mark.ws
@pytest.mark.destructive
def test_create_and_delete_dscenario(client, default_params):
    """Create a dscenario using the DB function and then delete it."""
    assert_ready(client)

    dscenario_id = _create_dscenario(client, default_params)

    response = client.delete(api(f"/epa/dscenarios/{dscenario_id}"), params=default_params)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"


@pytest.mark.ws
def test_delete_dscenario_not_found(client, default_params):
    """Deleting a non-existing dscenario should return 404."""
    assert_ready(client)

    response = client.delete(api("/epa/dscenarios/999999"), params=default_params)

    assert response.status_code == 404
    assert response.json()["detail"] == "Dscenario not found"
