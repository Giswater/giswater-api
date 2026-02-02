"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Path
from ...utils.utils import (
    create_body_dict,
    execute_procedure,
    create_log,
    handle_procedure_result,
    execute_sql_select,
    get_db_version,
)
from ...models.om.waterbalance_models import (
    GetDmasResponse,
    GetDmaHydrometersResponse,
    GetDmaParametersResponse,
    GetDmaFlowmetersResponse,
)
from ...dependencies import CommonsDep

router = APIRouter(prefix="/waterbalance", tags=["OM - Water Balance"])


@router.get(
    "/dmas",
    description="Returns a collection of DMAs.",
    response_model=GetDmasResponse,
    response_model_exclude_unset=True,
)
async def get_dmas(
    commons: CommonsDep,
):
    log = create_log(__name__)

    body = create_body_dict(device=commons["device"], cur_user=commons["user_id"])

    result = await execute_procedure(
        log, commons["db_manager"], "gw_fct_getdmas", body, schema=commons["schema"], api_version=commons["api_version"]
    )
    return handle_procedure_result(result)


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
    # TODO: Add limit and offset
    # limit: int = Query(
    #     ...,
    #     title="Limit",
    #     description="The maximum number of hydrometers to fetch",
    #     examples=[100]
    # ),
    # offset: int = Query(
    #     ...,
    #     title="Offset",
    #     description="The number of hydrometers to skip",
    #     examples=[0, 100, 200]
    # ),
):
    log = create_log(__name__)

    parameters = {"dma_id": dma_id}
    body = create_body_dict(device=commons["device"], extras={"parameters": parameters}, cur_user=commons["user_id"])

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getdmahydrometers",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


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
    log = create_log(__name__)  # noqa: F841
    return {"message": "Fetched DMA parameters successfully"}


@router.get(
    "/dmas/{dma_id}/flowmeters",
    description=(
        "Returns a collection of flowmeters within a specific DMA, "
        "providing details on their location, status, and flow data."
    ),
    response_model=GetDmaFlowmetersResponse,
    response_model_exclude_unset=True,
)
async def get_dma_flowmeters(
    commons: CommonsDep,
    dma_id: int = Path(
        ..., title="DMA ID", description="The unique identifier of the DMA for which to fetch flowmeters", examples=[1]
    ),
    # TODO: Add limit and offset
    # limit: int = Query(
    #     ...,
    #     title="Limit",
    #     description="The maximum number of flowmeters to fetch",
    #     examples=[100]
    # ),
    # offset: int = Query(
    #     ...,
    #     title="Offset",
    #     description="The number of flowmeters to skip",
    #     examples=[0, 100, 200]
    # ),
):
    log = create_log(__name__)

    table_name = "om_waterbalance_dma_graph"
    flowmeters = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name=table_name,
        columns=["node_id", "flow_sign"],
        where_clause="dma_id = %s",
        parameters=(dma_id,),
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched DMA flowmeters successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"flowmeters": flowmeters}},
    }


@router.get(
    "/dmas/{dma_id}/connecs",
    description=("Returns a collection of connecs within a specific DMA, providing details from ve_connec."),
    response_model=GetDmaHydrometersResponse,
    response_model_exclude_unset=True,
)
async def get_dma_connecs(
    commons: CommonsDep,
    dma_id: int = Path(
        ..., title="DMA ID", description="The unique identifier of the DMA for which to fetch connecs", examples=[1]
    ),
):
    log = create_log(__name__)

    table_name = "ve_connec"
    hydrometers = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name=table_name,
        columns=None,  # Select all columns
        where_clause="dma_id = %s",
        parameters=(dma_id,),
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched DMA hydrometers successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"hydrometers": hydrometers}},
    }
