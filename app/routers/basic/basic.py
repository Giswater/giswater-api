"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query, Depends, HTTPException
from datetime import date
from typing import Literal, Union, Optional
import json
from pydantic import ValidationError
from ...utils.routing_utils import get_valhalla_route, get_geojson_from_route
from ...utils.utils import create_body_dict, execute_procedure, create_log, app
from ...dependencies import get_schema
from ...models.basic.basic_models import (
    GetInfoFromCoordinatesResponse,
    GetSelectorsResponse,
    GetObjectHydraulicOrderResponse,
    ShortestPathParams,
    GetObjectShortestPathOrderResponse,
    Location,
    GetFeatureChangesResponse,
    GetSearchResponse
)
from ...models.util_models import CoordinatesModel, GwErrorResponse

router = APIRouter(prefix="/basic", tags=["Basic"])


@router.get(
    "/getfeaturechanges",
    description="Fetch GIS features that have been modified since the date specified in the lastFeeding parameter.",
    response_model=Union[GetFeatureChangesResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def get_feature_changes(
    schema: str = Depends(get_schema),
    feature_type: Literal["FEATURE", "ELEMENT"] = Query(
        ...,
        alias="featureType",
        title="Feature Type",
        description="Type of feature to fetch"
    ),
    action: Literal["INSERT", "UPDATE"] = Query(
        ...,
        title="Action",
        description="Indicate wether to fetch inserts or updates"
    ),
    lastFeeding: date = Query(
        ...,
        title="Last Feeding",
        description="Last feeding date of the feature",
        example="2024-11-11"
    ),
):
    log = create_log(__name__)

    body = create_body_dict(
        feature={"feature_type": feature_type},
        extras={
            "action": action,
            "lastFeeding": lastFeeding.strftime("%Y-%m-%d")
        }
    )
    result = execute_procedure(log, "gw_fct_featurechanges", body, schema=schema)
    if not result:
        return {
            "status": "Failed",
            "message": {"level": 4, "text": "No feature changes found"},
            "version": {"db": "4.0.001", "api": app.version},
            "body": {
                "feature": []
            }
        }
    return result


@router.get(
    "/getinfofromcoordinates",
    description="Fetch GIS features that have been modified since the date specified in the lastFeeding parameter.",
    response_model=Union[GetInfoFromCoordinatesResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def get_info_from_coordinates(
    schema: str = Depends(get_schema),
    coordinates: CoordinatesModel = Query(..., description="Coordinates of the info")
):
    log = create_log(__name__)

    coordinates_dict = coordinates.model_dump()

    body = create_body_dict(
        form={"editable": "False"},
        feature={},
        extras={
            "activeLayer": "v_edit_node",
            "visibleLayers": [
                "v_edit_node", "v_edit_connec", "v_edit_arc", "v_edit_link", "v_edit_dimensions", "ext_municipality",
                "v_ext_streetaxis", "v_ext_plot"
            ],
            "coordinates": coordinates_dict
        }
    )

    result = execute_procedure(log, "gw_fct_getinfofromcoordinates", body, schema=schema)
    return result


@router.get(
    "/getselectors",
    description="Fetch current selectors",
    response_model=Union[GetSelectorsResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def get_selectors(
    schema: str = Depends(get_schema),
    selectorType: Literal["selector_basic", "selector_mincut", "selector_netscenario"] = Query(
        "selector_basic",
        title="Selector type",
        description="Type of selector to fetch"
    ),
    filterText: str = Query(
        "",
        title="Filter text",
        description="Filter text to apply to the selector"
    ),
    currentTab: Optional[str] = Query(
        None,
        title="Current tab",
        description="Current tab to fetch"
    )
):
    log = create_log(__name__)

    body = create_body_dict(
        form={"currentTab": currentTab},
        feature={},
        extras={"selectorType": selectorType, "filterText": filterText}
    )

    result = execute_procedure(log, "gw_fct_getselectors", body, schema=schema)
    return result


@router.get(
    "/getsearch",
    description="Search features",
    response_model=Union[GetSearchResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def get_search(
    schema: str = Depends(get_schema),
    searchText: str = Query(
        "",
        title="Search text",
        description="Text to search for"
    )
):
    log = create_log(__name__)

    body = create_body_dict(
        form={},
        feature={},
        filter_fields={"searchText": searchText}
    )

    result = execute_procedure(log, "gw_fct_getselectors", body, schema=schema)
    return result


@router.get(
    "/getobjecthydraulicorder",
    description=(
        "Get hydraulic order information for the specified object"
    ),
    response_model=GetObjectHydraulicOrderResponse,
    response_model_exclude_unset=True
)
async def get_object_hydraulic_order(
    schema: str = Depends(get_schema),
    objectType: Literal['VALVULA', 'DEPOSITO', 'TUBERIA', 'CLORADOR'] = Query(
        ...,
        title="Object type",
        description="Type of the object"
    ),
):

    result = {
        "status": "Accepted",
        "message": {"level": 4, "text": "Process done successfully"},
        "version": {"db": "4.0.001", "api": "0.2.0"},
        "body": {
            "data": {
                "hydraulicOrder": 1,
                "objectId": "123",
                "objectType": "VALVULA",
                "parentId": None,
                "children": []
            }
        }
    }
    return result


@router.get(
    "/getobjectshortestpathorder",
    description=(
        "Get shortest path between two points using Valhalla routing engine"
    ),
    response_model=GetObjectShortestPathOrderResponse,
    response_model_exclude_unset=True
)
async def get_object_shortest_path_order(
    schema: str = Depends(get_schema),
    locations: str = Query(
        ...,
        title="Locations",
        description="JSON array of locations to route between",
        example='[{"x":418777.3,"y":4576692.9,"epsg":25831},{"x":419019.0,"y":4576692.9,"epsg":25831}]'
    ),
    costing: Literal["auto", "pedestrian", "bicycle"] = Query(
        "auto",
        title="Costing",
        description="Mode of transport for the route",
        examples=["auto", "pedestrian", "bicycle"]
    ),
    units: Literal["miles", "kilometers"] = Query(
        "kilometers",
        title="Units",
        description="Units for distance measurements",
        examples=["kilometers", "miles"]
    ),
):
    try:
        # Parse the locations JSON string and convert to Location objects
        locations_data = [Location(**loc) for loc in json.loads(locations)]

        # Create a ShortestPathParams instance to validate the input
        params = ShortestPathParams(
            locations=locations_data,
            costing=costing,
            units=units
        )

        valhalla_params = {
            "locations": [location.to_dict() for location in locations_data],
            "costing": params.costing,
            "units": params.units,
        }
        # Get the route from Valhalla API
        valhalla_response, route = get_valhalla_route(valhalla_params)
        try:
            geojson_response = get_geojson_from_route(route, costing)
        except Exception:
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

        result = {
            "status": "Accepted",
            "message": {"level": 1, "text": status_message},
            "version": {"db": "4.0.001", "api": "0.2.0"},
            "body": {
                "data": {
                    "distance": distance,
                    "duration": duration,
                    "path": geojson_response,
                }
            }
        }
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid JSON format for locations parameter"
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    return result
