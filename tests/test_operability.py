"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from tests.helpers import assert_ready


def test_operability_smoke(client):
    """Post-deploy style checks: global health, tenant ready, admin list (requires DB in CI)."""
    assert_ready(client)
    r = client.get(
        "/admin/tenants",
        headers={"host": "bgeo360.com"},
        auth=("admin", "admin"),
    )
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
