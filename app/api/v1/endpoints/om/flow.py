"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import Literal, Optional

from fastapi import APIRouter, Body

from app.api.deps import CommonsDep, get_service_context
from app.schemas.common import CoordinatesModel
from app.schemas.om.flow_models import FlowResponse
from app.services.om.flow_service import FlowService

router = APIRouter(prefix="/om", tags=["OM - Flow"])


@router.post(
    "/flow",
    description="Calculate flow trace (upstream) or flow exit (downstream)",
    response_model=FlowResponse,
    response_model_exclude_unset=True,
)
async def flow(
    commons: CommonsDep,
    direction: Literal["upstream", "downstream"] = Body(..., description="Flow direction"),
    node_id: Optional[int] = Body(None, description="Node ID", examples=[35]),
    coordinates: Optional[CoordinatesModel] = Body(
        None,
        description="Coordinates of the node to calculate the flow trace",
    ),
):
    """Calculate flow trace"""
    ctx = get_service_context(commons)
    return await FlowService(ctx).flow(direction, node_id, coordinates)
