"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import asyncio
import os
import sys

# Force test-specific globals BEFORE app.main is imported so the lifespan
# loads tenants from the fixtures directory.
os.environ.setdefault("BASE_DOMAIN", "bgeo360.com")
os.environ.setdefault("TENANTS_DIR", "tests/fixtures/tenants")
os.environ.setdefault("ADMIN_USER", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin")
os.environ.setdefault("LOG_DB_ENABLED", "false")
os.environ.setdefault("GISWATER_DB_VERSION_CHECK", "false")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
def default_headers() -> dict[str, str]:
    return {"X-Device": "5", "X-Lang": "en_US"}


@pytest.fixture
def default_params() -> dict[str, str]:
    return {"schema": os.getenv("DB_SCHEMA", "public")}


@pytest.fixture
def client(default_headers: dict[str, str]):
    with TestClient(app, base_url="http://test.bgeo360.com", headers=default_headers) as c:
        yield c
