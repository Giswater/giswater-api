"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from __future__ import annotations

from typing import Literal, Optional

from app.schemas.common import CoordinatesModel
from app.services.context import ServiceContext
from app.services.procedure import run_procedure
from app.utils.body import create_body_dict


class FlowService:
    def __init__(self, ctx: ServiceContext):
        self.ctx = ctx.with_logger(__name__)

    async def flow(
        self,
        direction: Literal["upstream", "downstream"],
        node_id: Optional[int],
        coordinates: Optional[CoordinatesModel],
    ) -> dict:
        if coordinates:
            coordinates_dict = coordinates.model_dump()
        else:
            coordinates_dict = None

        feature = None
        extras = None
        if node_id:
            feature = {"id": [node_id]}
        elif coordinates_dict:
            extras = {"coordinates": coordinates_dict}
        else:
            raise ValueError("Either node ID or coordinates must be provided")

        body = create_body_dict(
            device=self.ctx.device,
            feature=feature,
            extras=extras,
            cur_user=self.ctx.user_id,
        )

        procedure = "gw_fct_graphanalytics_upstream"
        if direction == "downstream":
            procedure = "gw_fct_graphanalytics_downstream"

        return await run_procedure(self.ctx, procedure, body)
