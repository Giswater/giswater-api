"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from datetime import date
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.schemas.basic.basic_models import (
    GetArcAuditValuesResponse,
    GetFeatureChangesResponse,
    GetFeaturesFromPolygonResponse,
    GetInfoFromCoordinatesResponse,
    GetListResponse,
    GetSearchResponse,
    GetSelectorsResponse,
)
from app.schemas.common import CoordinatesModel
from app.services.basic_service import BasicService
from app.services.context import service_context_from_commons

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
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_feature_changes(feature_type, action, last_feeding)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/getinfofromcoordinates",
    description="Get feature information from coordinates",
    response_model=GetInfoFromCoordinatesResponse,
    response_model_exclude_unset=True,
)
async def get_info_from_coordinates(
    commons: CommonsDep, coordinates: CoordinatesModel = Query(..., description="Coordinates of the info")
):
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_info_from_coordinates(coordinates)
    except Exception as exc:
        raise map_service_error(exc) from exc


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
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_features_from_polygon(feature_type, polygon_geom)
    except Exception as exc:
        raise map_service_error(exc) from exc


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
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_selectors(selector_type, filter_text, current_tab)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get(
    "/getsearch", description="Search features", response_model=GetSearchResponse, response_model_exclude_unset=True
)
async def get_search(
    commons: CommonsDep,
    search_text: str = Query("", alias="searchText", title="Search text", description="Text to search for"),
):
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_search(search_text)
    except Exception as exc:
        raise map_service_error(exc) from exc


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
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_arc_audit_values(start_date, end_date)
    except Exception as exc:
        raise map_service_error(exc) from exc


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
    try:
        ctx = service_context_from_commons(commons)
        return await BasicService(ctx).get_list(table_name, coordinates, page_info, filter_fields)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.get("/exploitations/{exploitation}")
async def get_exploitations(commons: CommonsDep, exploitation: str):
    """Not implemented."""
    raise HTTPException(status_code=501, detail="Method not implemented")
