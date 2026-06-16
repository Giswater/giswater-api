"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Query
from typing import Literal, Optional

from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.schemas.routing.routing_models import (
    GetObjectOptimalPathOrderResponse,
    GetObjectParameterOrderResponse,
)
from app.services.context import service_context_from_commons
from app.services.routing_service import RoutingService

router = APIRouter(prefix="/routing", tags=["OM - Routing"])


@router.get(
    "/getobjectoptimalpathorder",
    description=("Get optimal path through a network of points using Valhalla routing engine"),
    response_model=GetObjectOptimalPathOrderResponse,
    response_model_exclude_unset=True,
)
async def get_object_optimal_path_order(
    commons: CommonsDep,
    object_type: Literal[
        "EXPANSIONTANK",
        "FILTER",
        "FLEXUNION",
        "HYDRANT",
        "JUNCTION",
        "METER",
        "NETELEMENT",
        "NETSAMPLEPOINT",
        "NETWJOIN",
        "PUMP",
        "REDUCTION",
        "REGISTER",
        "SOURCE",
        "TANK",
        "VALVE",
        "WATERWELL",
    ] = Query(..., alias="objectType", title="Object type", description="Type of the object"),
    mapzone_type: Literal["EXPLOITATION", "SECTOR"] = Query(
        ..., alias="mapzoneType", title="Mapzone type", description="Type of the mapzone"
    ),
    mapzone_id: int = Query(..., alias="mapzoneId", title="Mapzone ID", description="ID of the mapzone"),
    initial_point: str = Query(
        '{"x": 419436.50, "y": 4576993.97, "epsg": 25831}',
        description='Initial point as JSON string (e.g., \'{"x": 419436.50, "y": 4576993.97, "epsg": 25831}\')',
        alias="initialPoint",
    ),
    final_point: Optional[str] = Query(
        None,
        description='Final point as JSON string (e.g., \'{"x": 419251.83, "y": 4576127.70, "epsg": 25831}\')',
        alias="finalPoint",
    ),
    transport_mode: Literal["auto", "pedestrian", "bicycle"] = Query(
        "auto",
        alias="transportMode",
        title="Transport mode",
        description="Mode of transport for the path",
        examples=["auto", "pedestrian", "bicycle"],
    ),
    units: Literal["miles", "kilometers"] = Query(
        "kilometers", title="Units", description="Units for distance measurements", examples=["kilometers", "miles"]
    ),
    language: Literal[
        "bg-BG",
        "ca-ES",
        "cs-CZ",
        "da-DK",
        "de-DE",
        "el-GR",
        "en-GB",
        "en-US-x-pirate",
        "en-US",
        "es-ES",
        "et-EE",
        "fi-FI",
        "fr-FR",
        "hi-IN",
        "hu-HU",
        "it-IT",
        "ja-JP",
        "nb-NO",
        "nl-NL",
        "pl-PL",
        "pt-BR",
        "pt-PT",
        "ro-RO",
        "ru-RU",
        "sk-SK",
        "sl-SI",
        "sv-SE",
        "tr-TR",
        "uk-UA",
    ] = Query(
        "en-US",
        title="Language",
        description="Language for the response",
    ),
):
    try:
        ctx = service_context_from_commons(commons)
        return await RoutingService(ctx).get_object_optimal_path_order(
            object_type, mapzone_type, mapzone_id, initial_point, final_point, transport_mode, units, language
        )
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/getobjectparameterorder",
    description=("Get features ordered by a parameter"),
    response_model=GetObjectParameterOrderResponse,
    response_model_exclude_unset=True,
)
async def get_object_parameter_order(
    commons: CommonsDep,
    object_type: Literal[
        "EXPANSIONTANK",
        "FILTER",
        "FLEXUNION",
        "HYDRANT",
        "JUNCTION",
        "METER",
        "NETELEMENT",
        "NETSAMPLEPOINT",
        "NETWJOIN",
        "PUMP",
        "REDUCTION",
        "REGISTER",
        "SOURCE",
        "TANK",
        "VALVE",
        "WATERWELL",
    ] = Query(..., alias="objectType", title="Object type", description="Type of the object"),
    mapzone_type: Literal["EXPLOITATION", "SECTOR"] = Query(
        ..., alias="mapzoneType", title="Mapzone type", description="Type of the mapzone"
    ),
    mapzone_id: int = Query(
        ..., alias="mapzoneId", title="Mapzone ID", description="ID of the mapzone", examples=[1, 2]
    ),
    parameter: str = Query(
        ...,
        title="Parameter",
        description="Parameter to order by",
        examples=["node_id", "nodecat_id, node_id", "builtdate", "top_elev"],
    ),
    order: Literal["asc", "desc"] = Query("asc", title="Order", description="Order of the parameter"),
):
    try:
        ctx = service_context_from_commons(commons)
        return await RoutingService(ctx).get_object_parameter_order(
            object_type, mapzone_type, mapzone_id, parameter, order
        )
    except Exception as exc:
        raise map_service_error(exc) from exc
