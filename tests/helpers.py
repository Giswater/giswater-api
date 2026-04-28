"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi.testclient import TestClient


def assert_ready(client: TestClient) -> None:
    health = client.get("/health").json()
    assert health.get("status") == "ok", f"Health check failed: {health}"
    ready = client.get("/ready").json()
    assert ready.get("status") == "ready", f"Ready check failed: {ready}"
