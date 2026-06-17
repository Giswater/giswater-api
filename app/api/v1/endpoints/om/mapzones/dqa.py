"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from app.api.deps import CommonsDep, get_service_context
from app.schemas.om.mapzone_models import GetMacrodqasResponse, GetDqasResponse
from app.services.om.mapzones_service import MapzonesService

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/macrodqas",
    description="Returns a collection of macrodqas.",
    response_model=GetMacrodqasResponse,
    response_model_exclude_unset=True,
)
async def get_macrodqas(commons: CommonsDep):
    ctx = get_service_context(commons)
    return await MapzonesService(ctx).get_macrodqas()


@router.get(
    "/dqas",
    description="Returns a collection of dqas.",
    response_model=GetDqasResponse,
    response_model_exclude_unset=True,
)
async def get_dqas(commons: CommonsDep):
    ctx = get_service_context(commons)
    return await MapzonesService(ctx).get_dqas()
