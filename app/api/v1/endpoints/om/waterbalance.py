"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Query

from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.schemas.om.waterbalance_models import GetWaterbalanceResponse
from app.services.context import service_context_from_commons
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
    try:
        ctx = service_context_from_commons(commons)
        return await WaterbalanceService(ctx).get_waterbalance(dma_id)
    except Exception as exc:
        raise map_service_error(exc) from exc
