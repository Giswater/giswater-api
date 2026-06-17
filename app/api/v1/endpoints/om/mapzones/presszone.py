"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from app.api.deps import CommonsDep, get_service_context
from app.schemas.om.mapzone_models import GetPresszonesResponse
from app.services.om.mapzones_service import MapzonesService

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/presszones",
    description="Returns a collection of presszones.",
    response_model=GetPresszonesResponse,
    response_model_exclude_unset=True,
)
async def get_presszones(commons: CommonsDep):
    ctx = get_service_context(commons)
    return await MapzonesService(ctx).get_presszones()
