"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import json
from fastapi import APIRouter, Query, HTTPException
from pydantic import ValidationError
from datetime import date
from typing import Literal, Optional
from ...utils.utils import create_body_dict, execute_procedure, create_log, handle_procedure_result
from ...dependencies import CommonsDep
from ...models.basic.basic_models import (
    GetInfoFromCoordinatesResponse,
    GetSelectorsResponse,
    GetFeatureChangesResponse,
    GetSearchResponse,
    GetListResponse
)
from ...models.util_models import CoordinatesModel, ExtentModel, PageInfoModel, FilterFieldModel

router = APIRouter(prefix="/basic", tags=["Basic"])


@router.get(
    "/getfeaturechanges",
    description="Fetch GIS features that have been modified since the date specified in the lastFeeding parameter.",
    response_model=GetFeatureChangesResponse,
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
    response_model=GetInfoFromCoordinatesResponse,
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
    return handle_procedure_result(result)


@router.get(
    "/getselectors",
    description="Fetch current selectors",
    response_model=GetSelectorsResponse,
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
    return handle_procedure_result(result)


@router.get(
    "/getsearch",
    description="Search features",
    response_model=GetSearchResponse,
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
    return handle_procedure_result(result)


@router.get(
    "/getlist",
    description="Fetch a list of features",
    response_model=GetListResponse,
    response_model_exclude_unset=True
)
async def get_list(
    commons: CommonsDep,
    tableName: str = Query(
        ...,
        title="Table Name",
        description="Name of the table or view to query",
        examples=["ve_arc_pipe", "om_visit_x_arc"]
    ),
    coordinates: Optional[str] = Query(None, description="JSON string of coordinates (ExtentModel)"),
    pageInfo: Optional[str] = Query(None, description="JSON string of page info (PageInfoModel)"),
    filterFields: Optional[str] = Query(None, description="JSON string of filter fields (Dict[str, FilterFieldModel])"),
):
    """Get list"""
    log = create_log(__name__)

    # Parse JSON strings into models
    try:
        coordinates_data = None
        if coordinates:
            coords_obj = ExtentModel(**json.loads(coordinates))
            coordinates_data = coords_obj.model_dump(mode='json', exclude_unset=True)

        page_info_data = None
        if pageInfo:
            page_obj = PageInfoModel(**json.loads(pageInfo))
            page_info_data = page_obj.model_dump(mode='json', exclude_unset=True)

        filterFields_data = None
        if filterFields:
            filterFields = json.loads(filterFields)
            filterFields_data = {
                k: FilterFieldModel(**v).model_dump(mode='json', exclude_unset=True) for k, v in filterFields.items()
            }
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    data = {
        "tableName": tableName
    }
    if coordinates:
        data["canvasExtend"] = coordinates_data

    # Build the body
    body = create_body_dict(
        extras=data,
        filter_fields=filterFields_data if filterFields_data else {},
        pageInfo=page_info_data if page_info_data else {},
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getlist",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    return handle_procedure_result(result)
