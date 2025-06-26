"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Literal
import json
from pydantic import ValidationError
from ...utils.routing_utils import (
    get_network_points,
    get_valhalla_optimized_route,
    get_geojson_from_optimized_route,
    get_maneuvers
)
from ...utils.utils import create_body_dict, execute_procedure, create_log
from ...dependencies import get_schema
from ...models.routing.routing_models import (
    # GetObjectHydraulicOrderResponse,
    OptimalPathParams,
    GetObjectOptimalPathOrderResponse,
    Location,
    GetObjectParameterOrderResponse,
)
# from ...models.util_models import CoordinatesModel, GwErrorResponse

router = APIRouter(prefix="/routing", tags=["OM - Routing"])


# @router.get(
#     "/getobjecthydraulicorder",
#     description=(
#         "Get hydraulic order information for the specified object"
#     ),
#     response_model=GetObjectHydraulicOrderResponse,
#     response_model_exclude_unset=True
# )
# async def get_object_hydraulic_order(
#     schema: str = Depends(get_schema),
#     objectType: Literal['VALVULA', 'DEPOSITO', 'TUBERIA', 'CLORADOR'] = Query(
#         ...,
#         title="Object type",
#         description="Type of the object"
#     ),
# ):

#     result = {
#         "status": "Accepted",
#         "message": {"level": 4, "text": "Process done successfully"},
#         "version": {"db": "4.0.001", "api": "0.2.0"},
#         "body": {
#             "data": {
#                 "hydraulicOrder": 1,
#                 "objectId": "123",
#                 "objectType": "VALVULA",
#                 "parentId": None,
#                 "children": []
#             }
#         }
#     }
#     return result


@router.get(
    "/getobjectoptimalpathorder",
    description=(
        "Get optimal path through a network of points using Valhalla routing engine"
    ),
    response_model=GetObjectOptimalPathOrderResponse,
    response_model_exclude_unset=True
)
async def get_object_optimal_path_order(
    schema: str = Depends(get_schema),
    objectType: Literal['EXPANSIONTANK', 'FILTER', 'FLEXUNION', 'HYDRANT',
                        'JUNCTION', 'METER', 'NETELEMENT', 'NETSAMPLEPOINT',
                        'NETWJOIN', 'PUMP', 'REDUCTION', 'REGISTER', 'SOURCE',
                        'TANK', 'VALVE', 'WATERWELL']
    = Query(
        ...,
        title="Object type",
        description="Type of the object"
    ),
    mapzoneType: Literal['EXPLOITATION', 'SECTOR'] = Query(
        ...,
        title="Mapzone type",
        description="Type of the mapzone"
    ),
    mapzoneId: int = Query(
        ...,
        title="Mapzone ID",
        description="ID of the mapzone"
    ),
    initialPoint: str = Query(
        '{"x": 419436.50, "y": 4576993.97, "epsg": 25831}',
        description="Initial point as JSON string (e.g., '{\"x\": 419436.50, \"y\": 4576993.97, \"epsg\": 25831}')",
        serialization_alias="initialPoint"
    ),
    finalPoint: str = Query(
        '{"x": 419251.83, "y": 4576127.70, "epsg": 25831}',
        description="Final point as JSON string (e.g., '{\"x\": 419251.83, \"y\": 4576127.70, \"epsg\": 25831}')",
        serialization_alias="finalPoint"
    ),
    transportMode: Literal["auto", "pedestrian", "bicycle"] = Query(
        "auto",
        title="Transport mode",
        description="Mode of transport for the path",
        examples=["auto", "pedestrian", "bicycle"]
    ),
    units: Literal["miles", "kilometers"] = Query(
        "kilometers",
        title="Units",
        description="Units for distance measurements",
        examples=["kilometers", "miles"]
    ),
    language: Literal[
        "bg-BG", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR", "en-GB",
        "en-US-x-pirate", "en-US", "es-ES", "et-EE", "fi-FI", "fr-FR",
        "hi-IN", "hu-HU", "it-IT", "ja-JP", "nb-NO", "nl-NL", "pl-PL",
        "pt-BR", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sl-SI", "sv-SE",
        "tr-TR", "uk-UA"
    ] = Query(
        "en-US",
        title="Language",
        description="Language for the response",
        examples=[
            "bg-BG", "ca-ES", "cs-CZ", "da-DK", "de-DE", "el-GR", "en-GB",
            "en-US-x-pirate", "en-US", "es-ES", "et-EE", "fi-FI", "fr-FR",
            "hi-IN", "hu-HU", "it-IT", "ja-JP", "nb-NO", "nl-NL", "pl-PL",
            "pt-BR", "pt-PT", "ro-RO", "ru-RU", "sk-SK", "sl-SI", "sv-SE",
            "tr-TR", "uk-UA"
        ]
    ),
):
    log = create_log(__name__)

    try:
        # Parse the locations JSON strings and convert to Location objects
        initial_point_data = json.loads(initialPoint)
        final_point_data = json.loads(finalPoint)

        initial_point = Location(**initial_point_data)
        final_point = Location(**final_point_data)

        mapzone_type = mapzoneType
        if mapzone_type == "EXPLOITATION":
            mapzone_type = "EXPL"

        # Get the network of points
        json_result, network_points = get_network_points(objectType, mapzone_type, mapzoneId, log, schema)
        features = json_result["body"]["data"]["features"]

        locations_data = [initial_point, *network_points, final_point]
        # Create a ShortestPathParams instance to validate the input
        params = OptimalPathParams(
            locations=locations_data,
            costing=transportMode,
            units=units
        )

        valhalla_params = {
            "locations": [location.to_dict() for location in locations_data],
            "costing": params.costing,
            "units": params.units,
            "language": language,
        }
        # Get the route from Valhalla API
        valhalla_response, legs = get_valhalla_optimized_route(valhalla_params)
        print(json.dumps(valhalla_response))

        # Check if we got a valid response
        if not isinstance(valhalla_response, dict):
            raise HTTPException(
                status_code=500,
                detail="Invalid response from Valhalla API"
            )

        try:
            # Use the new function to create GeoJSON with multiple legs
            geojson_response = get_geojson_from_optimized_route(valhalla_response.get("trip", {}), params.costing)
        except Exception as e:
            print(f"Error creating GeoJSON from optimized route: {e}")
            geojson_response = {}

        try:
            distance = valhalla_response["trip"]["summary"]["length"]  # type: ignore
        except Exception:
            distance = None
        try:
            duration = valhalla_response["trip"]["summary"]["time"]  # type: ignore
        except Exception:
            duration = None
        # try:
        #     status = valhalla_response["trip"]["status"]  # type: ignore
        # except Exception:
        #     status = None
        try:
            status_message = valhalla_response["trip"]["status_message"]  # type: ignore
        except Exception:
            status_message = None

        # Add maneuvers information
        maneuvers = get_maneuvers(valhalla_response)

        result = {
            "status": "Accepted",
            "message": {"level": 1, "text": status_message},
            "version": {"db": "4.0.001", "api": "0.2.0"},
            "body": {
                "data": {
                    "distance": distance,
                    "duration": duration,
                    "path": geojson_response,
                    "maneuvers": maneuvers,
                    "features": features,
                }
            }
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format for initialPoint or finalPoint parameter"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    return result


@router.get(
    "/getobjectparameterorder",
    description=(
        "Get features ordered by a parameter"
    ),
    response_model=GetObjectParameterOrderResponse,
    response_model_exclude_unset=True
)
async def get_object_parameter_order(
    schema: str = Depends(get_schema),
    objectType: Literal['EXPANSIONTANK', 'FILTER', 'FLEXUNION', 'HYDRANT',
                        'JUNCTION', 'METER', 'NETELEMENT', 'NETSAMPLEPOINT',
                        'NETWJOIN', 'PUMP', 'REDUCTION', 'REGISTER', 'SOURCE',
                        'TANK', 'VALVE', 'WATERWELL']
    = Query(
        ...,
        title="Object type",
        description="Type of the object"
    ),
    mapzoneType: Literal['EXPLOITATION', 'SECTOR'] = Query(
        ...,
        title="Mapzone type",
        description="Type of the mapzone"
    ),
    mapzoneId: int = Query(
        ...,
        title="Mapzone ID",
        description="ID of the mapzone",
        examples=[1, 2]
    ),
    parameter: str = Query(
        ...,
        title="Parameter",
        description="Parameter to order by",
        examples=["node_id", "nodecat_id, node_id", "builtdate", "top_elev"]
    ),
    order: Literal["asc", "desc"] = Query(
        "asc",
        title="Order",
        description="Order of the parameter"
    ),
):
    log = create_log(__name__)

    mapzone_type = mapzoneType
    if mapzone_type == "EXPLOITATION":
        mapzone_type = "EXPL"

    # Get the features from the database
    body = create_body_dict(
        extras={
            "sysType": objectType,
            "mapzoneType": mapzone_type,
            "mapzoneId": mapzoneId,
            "parameter": parameter,
            "order": order
        }
    )

    result = execute_procedure(log, "gw_fct_getfeatures_byparameter", body, schema=schema)

    # Get the network of points
    # network_points = get_network_points(objectType, mapzone_type, mapzoneId, log, schema)

    # locations_data = [initial_point, *network_points, final_point]
    # # Create a ShortestPathParams instance to validate the input
    # params = OptimalPathParams(
    #     locations=locations_data,
    #     costing=transportMode,
    #     units=units
    # )

    # valhalla_params = {
    #     "locations": [location.to_dict() for location in locations_data],
    #     "costing": params.costing,
    #     "units": params.units,
    # }
    # # Get the route from Valhalla API
    # valhalla_response, legs = get_valhalla_optimized_route(valhalla_params)

    # # Check if we got a valid response
    # if not isinstance(valhalla_response, dict):
    #     raise HTTPException(
    #         status_code=500,
    #         detail="Invalid response from Valhalla API"
    #     )

    # try:
    #     # Use the new function to create GeoJSON with multiple legs
    #     geojson_response = get_geojson_from_optimized_route(valhalla_response.get("trip", {}), params.costing)
    # except Exception as e:
    #     print(f"Error creating GeoJSON from optimized route: {e}")
    #     geojson_response = {}

    # try:
    #     distance = valhalla_response["trip"]["summary"]["length"]  # type: ignore
    # except Exception:
    #     distance = None
    # try:
    #     duration = valhalla_response["trip"]["summary"]["time"]  # type: ignore
    # except Exception:
    #     duration = None
    # # try:
    # #     status = valhalla_response["trip"]["status"]  # type: ignore
    # # except Exception:
    # #     status = None
    # try:
    #     status_message = valhalla_response["trip"]["status_message"]  # type: ignore
    # except Exception:
    #     status_message = None

    # # Add leg count information
    # leg_count = len(legs) if isinstance(legs, list) else 0

    # result = {
    #     "status": "Accepted",
    #     "message": {"level": 1, "text": status_message},
    #     "version": {"db": "4.0.001", "api": "0.2.0"},
    #     "body": {
    #         "data": {
    #             "distance": distance,
    #             "duration": duration,
    #             "path": geojson_response,
    #             "legCount": leg_count,
    #         }
    #     }
    # }
    return result
