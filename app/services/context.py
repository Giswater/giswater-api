"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from importlib.metadata import version as pkg_version

from app.db.context import DB_IDENTITY_CTX, DbIdentity
from app.db.manager import DatabaseManager
from app.tenancy.registry import Tenant


@dataclass(frozen=True)
class ServiceContext:
    tenant_id: str
    db_manager: DatabaseManager
    schema: str
    user_id: str | None
    db_role: str | None
    device: int = 5
    lang: str = "es_ES"
    api_version: str = pkg_version("giswater-api")
    logger: logging.Logger | None = None

    def with_logger(self, name: str) -> ServiceContext:
        from app.utils.log_setup import create_log

        return ServiceContext(
            tenant_id=self.tenant_id,
            db_manager=self.db_manager,
            schema=self.schema,
            user_id=self.user_id,
            db_role=self.db_role,
            device=self.device,
            lang=self.lang,
            api_version=self.api_version,
            logger=create_log(name),
        )

    def apply_db_identity(self) -> None:
        if self.user_id:
            DB_IDENTITY_CTX.set(DbIdentity(username=self.user_id, db_role=self.db_role))
        else:
            DB_IDENTITY_CTX.set(DbIdentity(username=None, db_role=None))


def service_context_from_commons(commons: dict) -> ServiceContext:
    tenant: Tenant = commons["tenant"]
    ctx = ServiceContext(
        tenant_id=tenant.id,
        db_manager=commons["db_manager"],
        schema=commons["schema"],
        user_id=commons["user_id"],
        db_role=commons["db_role"],
        device=commons["device"],
        lang=commons["lang"],
        api_version=commons["api_version"],
    )
    ctx.apply_db_identity()
    return ctx


def service_context_from_tenant(
    tenant: Tenant,
    *,
    schema: str,
    user_id: str | None = None,
    db_role: str | None = None,
    device: int = 5,
    lang: str = "es_ES",
) -> ServiceContext:
    ctx = ServiceContext(
        tenant_id=tenant.id,
        db_manager=tenant.db_manager,
        schema=schema,
        user_id=user_id,
        db_role=db_role,
        device=device,
        lang=lang,
    )
    ctx.apply_db_identity()
    return ctx
