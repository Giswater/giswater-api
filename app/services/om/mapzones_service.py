"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

from app.db.execution import execute_sql_select
from app.services.context import ServiceContext
from app.services.helpers import accepted_data_response


class MapzonesService:
    def __init__(self, ctx: ServiceContext):
        self.ctx = ctx.with_logger(__name__)

    async def _fetch_table(self, table_name: str, message: str, data_key: str) -> dict:
        rows = await execute_sql_select(
            self.ctx.logger,
            self.ctx.db_manager,
            table_name=table_name,
            columns=None,
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        return await accepted_data_response(self.ctx, message, {data_key: rows})

    async def get_macrosectors(self) -> dict:
        return await self._fetch_table("macrosector", "Fetched macrosectors successfully", "macrosectors")

    async def get_sectors(self) -> dict:
        return await self._fetch_table("sector", "Fetched sectors successfully", "sectors")

    async def get_macrodqas(self) -> dict:
        return await self._fetch_table("macrodqa", "Fetched macrodqas successfully", "macrodqas")

    async def get_dqas(self) -> dict:
        return await self._fetch_table("dqa", "Fetched dqas successfully", "dqas")

    async def get_presszones(self) -> dict:
        return await self._fetch_table("presszone", "Fetched presszones successfully", "presszones")

    async def get_macroomzones(self) -> dict:
        return await self._fetch_table("macroomzone", "Fetched macroomzones successfully", "macroomzones")

    async def get_omzones(self) -> dict:
        return await self._fetch_table("omzone", "Fetched omzones successfully", "omzones")

    async def get_omunits(self) -> dict:
        return await self._fetch_table("omunit", "Fetched omunits successfully", "omunits")
