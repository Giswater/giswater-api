"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.schemas.om.mapzone_models import GetMacrosectorsResponse, GetSectorsResponse
from app.services.context import service_context_from_commons
from app.services.om.mapzones_service import MapzonesService

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/macrosectors",
    description="Returns a collection of macrosectors.",
    response_model=GetMacrosectorsResponse,
    response_model_exclude_unset=True,
)
async def get_macrosectors(commons: CommonsDep):
    try:
        ctx = service_context_from_commons(commons)
        return await MapzonesService(ctx).get_macrosectors()
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/sectors",
    description="Returns a collection of sectors.",
    response_model=GetSectorsResponse,
    response_model_exclude_unset=True,
)
async def get_sectors(commons: CommonsDep):
    try:
        ctx = service_context_from_commons(commons)
        return await MapzonesService(ctx).get_sectors()
    except Exception as exc:
        raise map_service_error(exc) from exc
