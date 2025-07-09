"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query, Depends
from typing import Union
from ...utils.utils import create_body_dict, execute_procedure, create_log
from ...models.util_models import GwErrorResponse
from ...models.om.waterbalance_models import ListDmasResponse, GetDmaHydrometersResponse, GetDmaParametersResponse
from ...dependencies import get_schema

router = APIRouter(prefix="/waterbalance", tags=["OM - Water Balance"])


@router.get(
    "/listdmas",
    description="Returns a collection of DMAs.",
    response_model=Union[ListDmasResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def list_dmas(
    schema: str = Depends(get_schema),
):
    log = create_log(__name__)

    body = create_body_dict()

    result = execute_procedure(log, "gw_fct_getdmas", body, schema=schema)
    return result


@router.get(
    "/getdmahydrometers",
    description=(
        "Returns a collection of hydrometers within a specific DMA, "
        "providing details on their location, status, and measurement data."
    )
)
async def get_dma_hydrometers(
    dma_id: int = Query(
        ...,
        title="DMA ID",
        description="The unique identifier of the DMA for which to fetch hydrometers",
        examples=[1]
    ),
):
    return {"message": "Fetched DMA hydrometers successfully"}


@router.get(
    "/getdmaparameters",
    description=(
        "Retrieves specific parameters within a DMA, excluding geometry. "
        "Provides consumption data, network information, and other key metrics "
        "for performance analysis over a selected period."
    )
)
async def get_dma_parameters(
    dma_id: int = Query(
        ...,
        title="DMA ID",
        description="The unique identifier of the DMA for which to fetch parameters",
        examples=[1]
    ),
):
    return {"message": "Fetched DMA parameters successfully"}
