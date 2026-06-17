"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import logging

from ...core.config import TenantSettings, global_settings
from .gwapi import ensure_gwapi_schema
from .log import ensure_log_schema

logger = logging.getLogger(__name__)


async def ensure_tenant_schemas(db_manager, settings: TenantSettings) -> None:
    if global_settings.log_db_enabled:
        await ensure_log_schema(db_manager)
    if settings.auth_mode == "basic":
        await ensure_gwapi_schema(db_manager)
        from ...auth.users import maybe_bootstrap_user

        await maybe_bootstrap_user(db_manager, settings)
