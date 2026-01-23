"""
Copyright © 2026 by BGEO. All rights reserved.
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
    GetFeaturesFromPolygonResponse,
    GetSelectorsResponse,
    GetFeatureChangesResponse,
    GetSearchResponse,
    GetListResponse,
    GetArcAuditValuesResponse,
)
from ...models.util_models import CoordinatesModel, ExtentModel, PageInfoModel, FilterFieldModel

router = APIRouter(prefix="/basic", tags=["Basic"])


@router.get(
    "/getfeaturechanges",
    description="Fetch GIS features that have been modified since the date specified in the lastFeeding parameter.",
    response_model=GetFeatureChangesResponse,
    response_model_exclude_unset=True,
)
async def get_feature_changes(
    commons: CommonsDep,
    feature_type: Literal["FEATURE", "ARC", "NODE", "CONNEC", "GULLY", "ELEMENT"] = Query(
        ..., alias="featureType", title="Feature Type", description="Type of feature to fetch"
    ),
    action: Literal["INSERT", "UPDATE"] = Query(
        ..., title="Action", description="Indicate wether to fetch inserts or updates"
    ),
    last_feeding: date = Query(
        ...,
        alias="lastFeeding",
        title="Last Feeding",
        description="Last feeding date of the feature",
        examples=["2024-11-11"],
    ),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        feature={"feature_type": feature_type},
        extras={"action": action, "lastFeeding": last_feeding.strftime("%Y-%m-%d")},
        cur_user=commons["user_id"],
    )
    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_featurechanges",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
        user=commons["user_id"],
    )
    if not result:
        return {
            "status": "Failed",
            "message": {"level": 4, "text": "No feature changes found"},
            "version": {"api": commons["api_version"]},
            "body": {"feature": []},
        }
    return result


@router.get(
    "/getinfofromcoordinates",
    description="Get feature information from coordinates",
    response_model=GetInfoFromCoordinatesResponse,
    response_model_exclude_unset=True,
)
async def get_info_from_coordinates(
    commons: CommonsDep, coordinates: CoordinatesModel = Query(..., description="Coordinates of the info")
):
    log = create_log(__name__)

    coordinates_dict = coordinates.model_dump()

    body = create_body_dict(
        device=commons["device"],
        form={"editable": "False"},
        feature={},
        extras={
            "activeLayer": "ve_node",
            "visibleLayers": [
                "ve_cat_feature_node",
                "ve_cat_feature_arc",
                "ve_cat_feature_connec",
                "ve_cat_feature_gully",
                "ve_cat_feature_link",
                "ve_cat_feature_element",
                "cat_node",
                "cat_arc",
                "cat_connec",
                "cat_gully",
                "cat_link",
                "cat_element",
                "cat_material",
                "ve_node",
                "ve_man_frelem",
                "ve_arc",
                "ve_connec",
                "ve_gully",
                "ve_link",
                "ve_pol_node",
                "ve_pol_connec",
                "ve_pol_gully",
                "ve_dimensions",
                "v_ext_municipality",
                "v_ext_plot",
                "v_ext_streetaxis",
                "cat_feature",
                "sys_feature_type",
                "v_value_relation",
            ],
            "coordinates": coordinates_dict,
        },
        cur_user=commons["user_id"],
    )

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getinfofromcoordinates",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.get(
    "/getfeaturesfrompolygon",
    description="Get features from polygon",
    response_model=GetFeaturesFromPolygonResponse,
    response_model_exclude_unset=True,
)
async def get_features_from_polygon(
    commons: CommonsDep,
    feature_type: Literal["ARC", "NODE", "CONNEC", "GULLY", "ALL"] = Query(
        ..., alias="featureType", title="Feature Type", description="Type of feature to fetch"
    ),
    polygon_geom: str = Query(
        ...,
        alias="polygonGeom",
        title="Polygon Geometry",
        description="Geometry of the polygon in WKT format",
        examples=[
            "MULTIPOLYGON (((419419.13867777254 4576466.499338785, 419429.1574217372 4576487.650020488, 419537.69381468766 4576466.221040341, 419497.8971372725 4576396.368131032, 419419.13867777254 4576404.438785893, 419419.13867777254 4576466.499338785)))"
        ],  # noqa: E501
    ),
):
    log = create_log(__name__)

    parameters = {"featureType": feature_type, "polygonGeom": polygon_geom}
    body = create_body_dict(
        device=commons["device"], form={}, feature={}, extras={"parameters": parameters}, cur_user=commons["user_id"]
    )

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getfeaturesfrompolygon",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.get(
    "/getselectors",
    description="Fetch current selectors",
    response_model=GetSelectorsResponse,
    response_model_exclude_unset=True,
)
async def get_selectors(
    commons: CommonsDep,
    selector_type: Literal["selector_basic", "selector_mincut", "selector_netscenario"] = Query(
        "selector_basic", alias="selectorType", title="Selector type", description="Type of selector to fetch"
    ),
    filter_text: str = Query(
        "", alias="filterText", title="Filter text", description="Filter text to apply to the selector"
    ),
    current_tab: Optional[str] = Query(
        None, alias="currentTab", title="Current tab", description="Current tab to fetch"
    ),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        form={"currentTab": current_tab},
        feature={},
        extras={"selectorType": selector_type, "filterText": filter_text},
        cur_user=commons["user_id"],
    )

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getselectors",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.get(
    "/getsearch", description="Search features", response_model=GetSearchResponse, response_model_exclude_unset=True
)
async def get_search(
    commons: CommonsDep,
    search_text: str = Query("", alias="searchText", title="Search text", description="Text to search for"),
):
    log = create_log(__name__)

    parameters = {"searchText": search_text}

    body = create_body_dict(
        device=commons["device"], form={}, feature={}, extras={"parameters": parameters}, cur_user=commons["user_id"]
    )

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getsearch",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.get(
    "/getarcauditvalues",
    description="Fetch arc audit values",
    response_model=GetArcAuditValuesResponse,
    response_model_exclude_unset=True,
)
async def get_arc_audit_values(
    commons: CommonsDep,
    start_date: date = Query(
        ...,
        alias="startDate",
        title="Start Date",
        description="Start date for audit events",
        examples=["2026-01-01"],
    ),
    end_date: date = Query(
        ...,
        alias="endDate",
        title="End Date",
        description="End date for audit events",
        examples=["2026-01-31"],
    ),
):
    log = create_log(__name__)

    parameters = {"startDate": start_date.strftime("%Y-%m-%d"), "endDate": end_date.strftime("%Y-%m-%d")}
    body = create_body_dict(
        device=commons["device"],
        form={},
        feature={},
        extras={"parameters": parameters},
        cur_user=commons["user_id"],
    )

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getarcauditvalues",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
        user=commons["user_id"],
    )
    return handle_procedure_result(result)


@router.get(
    "/getlist",
    description="Fetch a list of features",
    response_model=GetListResponse,
    response_model_exclude_unset=True,
)
async def get_list(
    commons: CommonsDep,
    table_name: str = Query(
        ...,
        alias="tableName",
        title="Table Name",
        description="Name of the table or view to query",
        examples=["ve_arc_pipe", "om_visit_x_arc"],
    ),
    coordinates: Optional[str] = Query(None, description="JSON string of coordinates (ExtentModel)"),
    page_info: Optional[str] = Query(None, alias="pageInfo", description="JSON string of page info (PageInfoModel)"),
    filter_fields: Optional[str] = Query(
        None, alias="filterFields", description="JSON string of filter fields (Dict[str, FilterFieldModel])"
    ),
):
    """Get list"""
    log = create_log(__name__)

    # Parse JSON strings into models
    try:
        coordinates_data = None
        if coordinates:
            coords_obj = ExtentModel(**json.loads(coordinates))
            coordinates_data = coords_obj.model_dump(mode="json", exclude_unset=True)

        page_info_data = None
        if page_info:
            page_obj = PageInfoModel(**json.loads(page_info))
            page_info_data = page_obj.model_dump(mode="json", exclude_unset=True)

        filter_fields_data = None
        if filter_fields:
            filter_fields_raw = json.loads(filter_fields)
            filter_fields_data = {
                k: FilterFieldModel(**v).model_dump(mode="json", exclude_unset=True)
                for k, v in filter_fields_raw.items()
            }
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    data = {"tableName": table_name}
    if coordinates:
        data["canvasExtend"] = coordinates_data

    # Build the body
    body = create_body_dict(
        extras=data,
        filter_fields=filter_fields_data if filter_fields_data else {},
        page_info=page_info_data if page_info_data else {},
        cur_user=commons["user_id"],
    )

    result = await execute_procedure(
        log, commons["db_manager"], "gw_fct_getlist", body, schema=commons["schema"], api_version=commons["api_version"]
    )
    return handle_procedure_result(result)
