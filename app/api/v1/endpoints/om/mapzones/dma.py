"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Path

from app.schemas.om.dma_models import (
    GetDmasResponse,
    GetDmaHydrometersResponse,
    GetDmaParametersResponse,
    GetDmaConnecsResponse,
)
from app.schemas.om.mapzone_models import GetMacrodmasResponse
from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.services.context import service_context_from_commons
from app.services.om.dma_service import DmaService

router = APIRouter(prefix="/om", tags=["OM - District Metered Areas"])


@router.get(
    "/dmas",
    description="Returns a collection of DMAs.",
    response_model=GetDmasResponse,
    response_model_exclude_unset=True,
)
async def get_dmas(commons: CommonsDep):
    try:
        ctx = service_context_from_commons(commons)
        return await DmaService(ctx).get_dmas()
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/macrodmas",
    description="Returns a collection of macrodmas.",
    response_model=GetMacrodmasResponse,
    response_model_exclude_unset=True,
)
async def get_macrodmas(commons: CommonsDep):
    try:
        ctx = service_context_from_commons(commons)
        return await DmaService(ctx).get_macrodmas()
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/dmas/{dma_id}/hydrometers",
    description=(
        "Returns a collection of hydrometers within a specific DMA, "
        "providing details on their location, status, and measurement data."
    ),
    response_model=GetDmaHydrometersResponse,
    response_model_exclude_unset=True,
)
async def get_dma_hydrometers(
    commons: CommonsDep,
    dma_id: int = Path(
        ..., title="DMA ID", description="The unique identifier of the DMA for which to fetch hydrometers", examples=[1]
    ),
):
    try:
        ctx = service_context_from_commons(commons)
        return await DmaService(ctx).get_dma_hydrometers(dma_id)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/dmas/{dma_id}/parameters",
    description=(
        "Retrieves specific parameters within a DMA, excluding geometry. "
        "Provides consumption data, network information, and other key metrics "
        "for performance analysis over a selected period."
    ),
    response_model=GetDmaParametersResponse,
    response_model_exclude_unset=True,
)
async def get_dma_parameters(
    commons: CommonsDep,
    dma_id: int = Path(
        ..., title="DMA ID", description="The unique identifier of the DMA for which to fetch parameters", examples=[1]
    ),
):
    try:
        ctx = service_context_from_commons(commons)
        return await DmaService(ctx).get_dma_parameters(dma_id)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/dmas/{dma_id}/connecs",
    description=("Returns a collection of connecs within a specific DMA, providing details from ve_connec."),
    response_model=GetDmaConnecsResponse,
    response_model_exclude_unset=True,
)
async def get_dma_connecs(
    commons: CommonsDep,
    dma_id: int = Path(
        ..., title="DMA ID", description="The unique identifier of the DMA for which to fetch connecs", examples=[1]
    ),
):
    try:
        ctx = service_context_from_commons(commons)
        return await DmaService(ctx).get_dma_connecs(dma_id)
    except Exception as exc:
        raise map_service_error(exc) from exc
