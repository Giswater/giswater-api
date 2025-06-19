"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query

router = APIRouter(prefix="/waterbalance", tags=["OM - Water Balance"])


@router.get(
    "/listdmas",
    description="Returns a collection of DMAs."
)
async def list_dmas():
    dmas = [
        {"id": 1, "name": "DMA 1"},
        {"id": 2, "name": "DMA 2"},
        {"id": 3, "name": "DMA 3"},
    ]
    return {"dmas": dmas}


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
