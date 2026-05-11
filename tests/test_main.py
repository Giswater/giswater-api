"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from app.constants import ADMIN_PREFIX, GLOBAL_HEALTH_PATH

from tests.helpers import api


def test_get_status(client):
    response = client.get(api("/"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Accepted"


def test_health(client):
    response = client.get(GLOBAL_HEALTH_PATH)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_tenant_health(client):
    response = client.get(api("/health"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_admin_health(client):
    response = client.get(f"{ADMIN_PREFIX}/health", headers={"host": "bgeo360.com"}, auth=("admin", "admin"))
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_example_env_not_loaded_as_tenant(client):
    response = client.get(api("/health"), headers={"host": "example.bgeo360.com"})
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Unknown tenant 'example'"
