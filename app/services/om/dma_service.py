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
from app.services.procedure import run_procedure
from app.utils.body import create_body_dict

_DMA_CONNEC_COLUMNS = [
    "connec_id",
    "code",
    "sys_code",
    "top_elev",
    "connec_type",
    "sys_type",
    "conneccat_id",
    "cat_matcat_id",
    "cat_pnom",
    "cat_dnom",
    "cat_dint",
    "customer_code",
    "connec_length",
    "epa_type",
    "state",
    "state_type",
    "arc_id",
    "expl_id",
    "macroexpl_id",
    "muni_id",
    "sector_id",
    "macrosector_id",
    "sector_type",
    "supplyzone_id",
    "supplyzone_type",
    "presszone_id",
    "presszone_type",
    "presszone_head",
    "dma_id",
    "macrodma_id",
    "dma_type",
    "dqa_id",
    "macrodqa_id",
    "dqa_type",
    "omzone_id",
    "omzone_type",
    "crmzone_id",
    "macrocrmzone_id",
    "crmzone_name",
    "minsector_id",
    "soilcat_id",
    "function_type",
    "category_type",
    "location_type",
    "fluid_type",
    "n_hydrometer",
    "n_inhabitants",
    "staticpressure",
    "descript",
    "annotation",
    "observ",
    "comment",
    "link",
    "num_value",
    "district_id",
    "postcode",
    "streetaxis_id",
    "postnumber",
    "postcomplement",
    "streetaxis2_id",
    "postnumber2",
    "postcomplement2",
    "region_id",
    "province_id",
    "block_code",
    "plot_code",
    "workcat_id",
    "workcat_id_end",
    "workcat_id_plan",
    "builtdate",
    "enddate",
    "ownercat_id",
    "pjoint_id",
    "pjoint_type",
    "om_state",
    "conserv_state",
    "accessibility",
    "access_type",
    "placement_type",
    "priority",
    "brand_id",
    "model_id",
    "serial_number",
    "asset_id",
    "adate",
    "adescript",
    "verified",
    "datasource",
    "label",
    "label_x",
    "label_y",
    "label_rotation",
    "rotation",
    "label_quadrant",
    "svg",
    "inventory",
    "publish",
    "is_operative",
    "inp_type",
    "demand_base",
    "demand_max",
    "demand_min",
    "demand_avg",
    "press_max",
    "press_min",
    "press_avg",
    "quality_max",
    "quality_min",
    "quality_avg",
    "flow_max",
    "flow_min",
    "flow_avg",
    "vel_max",
    "vel_min",
    "vel_avg",
    "result_id",
    "sector_style",
    "dma_style",
    "presszone_style",
    "dqa_style",
    "supplyzone_style",
    "lock_level",
    "expl_visibility",
    "xcoord",
    "ycoord",
    "lat",
    "long",
    "created_at",
    "created_by",
    "updated_at",
    "updated_by",
    "the_geom",
    "p_state",
    "uuid",
    "uncertain",
    "xyz_date",
]


class DmaService:
    def __init__(self, ctx: ServiceContext):
        self.ctx = ctx.with_logger(__name__)

    async def get_dmas(self) -> dict:
        body = create_body_dict(device=self.ctx.device, cur_user=self.ctx.user_id)
        return await run_procedure(self.ctx, "gw_fct_getdmas", body)

    async def get_macrodmas(self) -> dict:
        macrodmas = await execute_sql_select(
            self.ctx.logger,
            self.ctx.db_manager,
            table_name="macrodma",
            columns=None,
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        return await accepted_data_response(self.ctx, "Fetched macrodmas successfully", {"macrodmas": macrodmas})

    async def get_dma_hydrometers(self, dma_id: int) -> dict:
        parameters = {"dma_id": dma_id}
        body = create_body_dict(device=self.ctx.device, extras={"parameters": parameters}, cur_user=self.ctx.user_id)
        return await run_procedure(self.ctx, "gw_fct_getdmahydrometers", body)

    async def get_dma_parameters(self, dma_id: int) -> dict:
        return {"message": "Fetched DMA parameters successfully"}

    async def get_dma_connecs(self, dma_id: int) -> dict:
        connecs = await execute_sql_select(
            self.ctx.logger,
            self.ctx.db_manager,
            table_name="ve_connec",
            columns=_DMA_CONNEC_COLUMNS,
            where_clause="dma_id = %s",
            parameters=(dma_id,),
            schema=self.ctx.schema,
            user=self.ctx.user_id,
            db_role=self.ctx.db_role,
        )
        return await accepted_data_response(self.ctx, "Fetched DMA connecs successfully", {"connecs": connecs})
