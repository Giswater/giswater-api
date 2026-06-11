"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

# Backward-compat tests for KEYCLOAK_ENABLED → AUTH_MODE shim.
# DEPRECATED #22: delete the legacy tests below when releasing 2.0.0 (grep DEPRECATED #22).

import warnings


from app.config import _build_tenant, _resolve_auth_mode
from app.models.auth_models import ApiUser


def test_resolve_auth_mode_explicit_none():
    assert _resolve_auth_mode({"AUTH_MODE": "none"}) == "none"


def test_resolve_auth_mode_explicit_basic():
    assert _resolve_auth_mode({"AUTH_MODE": "basic"}) == "basic"


# DEPRECATED #22: remove in 2.0.0
def test_resolve_auth_mode_keycloak_enabled_legacy():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert _resolve_auth_mode({"KEYCLOAK_ENABLED": "true"}) == "keycloak"
    assert any(issubclass(w.category, DeprecationWarning) for w in caught)


def test_resolve_auth_mode_default_none():
    assert _resolve_auth_mode({}) == "none"


# DEPRECATED #22: remove in 2.0.0
def test_build_tenant_auth_mode_from_keycloak_enabled():
    settings = _build_tenant({"KEYCLOAK_ENABLED": "true", "KEYCLOAK_URL": "https://auth.example.com"})
    assert settings.auth_mode == "keycloak"
    assert settings.keycloak_enabled is True


def test_api_user_roles():
    user = ApiUser(
        sub="1",
        preferred_username="alice",
        auth_method="basic",
        roles=frozenset({"role_basic", "role_edit"}),
        db_role="postgres",
    )
    assert user.has_role("role_edit")
    assert user.has_any_role(["role_om", "role_edit"])
    assert not user.has_role("role_master")


def test_api_user_anonymous():
    user = ApiUser.anonymous()
    assert user.is_anonymous
    assert not user.roles
