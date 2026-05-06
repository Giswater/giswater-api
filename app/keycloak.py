"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi_keycloak import FastAPIKeycloak

from .config import TenantSettings


def build_idp(tenant_settings: TenantSettings) -> FastAPIKeycloak | None:
    """Build a Keycloak IDP for a tenant, or return None when disabled."""
    if not tenant_settings.keycloak_enabled:
        return None
    return FastAPIKeycloak(
        server_url=tenant_settings.keycloak_url,
        client_id=tenant_settings.keycloak_client_id,
        client_secret=tenant_settings.keycloak_client_secret,
        admin_client_id=tenant_settings.keycloak_admin_client_id,
        admin_client_secret=tenant_settings.keycloak_admin_client_secret,
        realm=tenant_settings.keycloak_realm,
        callback_uri=tenant_settings.keycloak_callback_uri,
    )
