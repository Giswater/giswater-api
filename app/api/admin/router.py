"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import FastAPI

from app.api.admin import tenants, users


def register_admin(admin_app: FastAPI) -> None:
    """Include platform-admin routers on the admin sub-app."""
    admin_app.include_router(tenants.router)
    admin_app.include_router(users.router)
