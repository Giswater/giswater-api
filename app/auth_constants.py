"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

# Tracks 2.0.0 cleanup: grep `DEPRECATED #22` (github.com/Giswater/giswater-api/issues/22).
DEPRECATED_KEYCLOAK_ENABLED_ISSUE = "22"

AUTH_MODES = frozenset({"none", "basic", "keycloak"})

GWAPI_DEFAULT_ROLES: tuple[tuple[str, str], ...] = (
    ("role_basic", "Basic read access"),
    ("role_edit", "Edit access"),
    ("role_om", "Operations and maintenance"),
    ("role_epa", "EPA / scenario access"),
    ("role_master", "Master access"),
)

MIN_PASSWORD_LENGTH = 8
