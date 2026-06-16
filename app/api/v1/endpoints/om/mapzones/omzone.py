"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.schemas.om.mapzone_models import GetMacroomzonesResponse, GetOmzonesResponse
from app.services.context import service_context_from_commons
from app.services.om.mapzones_service import MapzonesService

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/macroomzones",
    description="Returns a collection of macroomzones.",
    response_model=GetMacroomzonesResponse,
    response_model_exclude_unset=True,
)
async def get_macroomzones(commons: CommonsDep):
    try:
        ctx = service_context_from_commons(commons)
        return await MapzonesService(ctx).get_macroomzones()
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/omzones",
    description="Returns a collection of omzones.",
    response_model=GetOmzonesResponse,
    response_model_exclude_unset=True,
)
async def get_omzones(commons: CommonsDep):
    try:
        ctx = service_context_from_commons(commons)
        return await MapzonesService(ctx).get_omzones()
    except Exception as exc:
        raise map_service_error(exc) from exc
