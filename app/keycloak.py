"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi_keycloak import FastAPIKeycloak, OIDCUser
from .config import settings

# Initialize Keycloak
idp = None
if settings.keycloak_enabled:
    idp = FastAPIKeycloak(
        server_url=settings.keycloak_url,
        client_id=settings.keycloak_client_id,
        client_secret=settings.keycloak_client_secret,
        admin_client_secret=settings.keycloak_admin_client_secret,
        realm=settings.keycloak_realm,
        callback_uri=settings.keycloak_callback_uri,
    )


# Dependency for routes - works with or without Keycloak
def get_current_user():
    """
    Returns a dependency for getting the current user.
    When Keycloak is enabled, validates token and returns OIDCUser.
    When disabled, returns anonymous user.
    """
    if idp:
        return idp.get_current_user()

    # Keycloak disabled - return anonymous user dependency
    async def anonymous_user() -> OIDCUser:
        return OIDCUser(sub="anonymous", iat=0, exp=0, email=None, email_verified=False, preferred_username="anonymous")

    return anonymous_user
