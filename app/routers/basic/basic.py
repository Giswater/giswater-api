"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query
from datetime import date
from typing import Literal, Union, Optional
from ...utils.utils import create_body_dict, execute_procedure, create_log
from ...dependencies import CommonsDep
from ...models.basic.basic_models import (
    GetInfoFromCoordinatesResponse,
    GetSelectorsResponse,
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
    commons: CommonsDep,
    feature_type: Literal["FEATURE", "ARC", "NODE", "CONNEC", "GULLY", "ELEMENT"] = Query(
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
        device=commons["device"],
        feature={"feature_type": feature_type},
        extras={
            "action": action,
            "lastFeeding": lastFeeding.strftime("%Y-%m-%d")
        },
        cur_user=commons["user_id"]
    )
    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_featurechanges",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
        user=commons["user_id"]
    )
    if not result:
        return {
            "status": "Failed",
            "message": {"level": 4, "text": "No feature changes found"},
            "version": {"api": commons["api_version"]},
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
    commons: CommonsDep,
    coordinates: CoordinatesModel = Query(..., description="Coordinates of the info")
):
    log = create_log(__name__)

    coordinates_dict = coordinates.model_dump()

    body = create_body_dict(
        device=commons["device"],
        form={"editable": "False"},
        feature={},
        extras={
            "activeLayer": "v_edit_node",
            "visibleLayers": [
                "v_edit_node", "v_edit_connec", "v_edit_arc", "v_edit_link", "v_edit_dimensions", "ext_municipality",
                "v_ext_streetaxis", "v_ext_plot"
            ],
            "coordinates": coordinates_dict
        },
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getinfofromcoordinates",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    return result


@router.get(
    "/getselectors",
    description="Fetch current selectors",
    response_model=Union[GetSelectorsResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def get_selectors(
    commons: CommonsDep,
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
        device=commons["device"],
        form={"currentTab": currentTab},
        feature={},
        extras={"selectorType": selectorType, "filterText": filterText},
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getselectors",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    return result


@router.get(
    "/getsearch",
    description="Search features",
    response_model=Union[GetSearchResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def get_search(
    commons: CommonsDep,
    searchText: str = Query(
        "",
        title="Search text",
        description="Text to search for"
    )
):
    log = create_log(__name__)

    parameters = {
        "searchText": searchText
    }

    body = create_body_dict(
        device=commons["device"],
        form={},
        feature={},
        extras={"parameters": parameters},
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getsearch",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    return result
