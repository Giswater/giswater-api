"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

from app.schemas.crm.crm_models import HydrometerCreate, HydrometerUpdate
from app.services.context import ServiceContext
from app.services.procedure import run_procedure
from app.utils.body import create_body_dict


class CrmService:
    def __init__(self, ctx: ServiceContext):
        self.ctx = ctx.with_logger(__name__)

    async def _set_hydrometers(self, action: str, hydrometers_data: list[dict]) -> dict:
        body = create_body_dict(
            device=self.ctx.device,
            extras={"action": action, "hydrometers": hydrometers_data},
            cur_user=self.ctx.user_id,
        )
        return await run_procedure(self.ctx, "gw_fct_set_hydrometers", body)

    async def insert_hydrometers(self, hydrometers: list[HydrometerCreate]) -> dict:
        hydrometers_data = [h.model_dump(mode="json", exclude_unset=True) for h in hydrometers]
        return await self._set_hydrometers("INSERT", hydrometers_data)

    async def update_hydrometer(self, code: str, hydrometer: HydrometerUpdate) -> dict:
        hydrometer_dict = hydrometer.model_dump(mode="json", exclude_unset=True)
        hydrometer_dict["code"] = code
        return await self._set_hydrometers("UPDATE", [hydrometer_dict])

    async def update_hydrometers_bulk(self, hydrometers: list[HydrometerUpdate]) -> dict:
        hydrometers_data = [h.model_dump(mode="json", exclude_unset=True) for h in hydrometers]
        return await self._set_hydrometers("UPDATE", hydrometers_data)

    async def delete_hydrometer(self, code: str) -> dict:
        return await self._set_hydrometers("DELETE", [{"code": code}])

    async def delete_hydrometers_bulk(self, codes: list[str]) -> dict:
        hydrometers_data = [{"code": code} for code in codes]
        return await self._set_hydrometers("DELETE", hydrometers_data)

    async def replace_all_hydrometers(self, hydrometers: list[HydrometerCreate]) -> dict:
        hydrometers_data = [h.model_dump(mode="json", exclude_unset=True) for h in hydrometers]
        return await self._set_hydrometers("REPLACE", hydrometers_data)
