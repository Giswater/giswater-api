"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import os
import asyncio
import sys

import pytest
from fastapi.testclient import TestClient

from app.main import app


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
    with TestClient(app, headers=default_headers) as client:
        yield client
