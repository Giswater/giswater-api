"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Query

from app.api.deps import CommonsDep, get_service_context
from app.schemas.om.waterbalance_models import GetWaterbalanceResponse
from app.services.om.waterbalance_service import WaterbalanceService

router = APIRouter(prefix="/om", tags=["OM - Water Balance"])


@router.get(
    "/waterbalance",
    description=("Returns the water balance graph for all DMAs."),
    response_model=GetWaterbalanceResponse,
    response_model_exclude_unset=True,
)
async def get_waterbalance(
    commons: CommonsDep,
    dma_id: list[int] | None = Query(None, title="DMA ID", description="Filter by DMA ID(s)", examples=[1]),
):
    ctx = get_service_context(commons)
    return await WaterbalanceService(ctx).get_waterbalance(dma_id)
