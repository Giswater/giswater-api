"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import Any, Dict, List, Optional, Union

from fastapi import APIRouter, Body, Path, Query

from app.api.deps import CommonsDep, get_service_context
from app.schemas.basic.basic_models import GetListResponse
from app.schemas.epa.dscenario_models import (
    DscenarioCreateRequest,
    DscenarioObjectResponse,
    DscenarioObjectType,
)
from app.services.epa.dscenario_service import DscenarioService

router = APIRouter(prefix="/epa", tags=["EPA - Dscenario"])


@router.post(
    "/dscenarios",
    description="Create an empty dscenario by calling gw_fct_create_dscenario_empty",
    response_model=dict,
    response_model_exclude_unset=True,
)
async def create_dscenario(
    commons: CommonsDep,
    payload: DscenarioCreateRequest = Body(..., description="Dscenario creation parameters"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).create_dscenario(payload)


@router.get(
    "/dscenarios",
    description="Get dscenarios",
    response_model=GetListResponse,
    response_model_exclude_unset=True,
)
async def get_dscenarios(
    commons: CommonsDep,
    filter_fields: Optional[str] = Query(None, alias="filterFields", description="Filter fields"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).get_dscenarios(filter_fields)


@router.post(
    "/dscenarios/{dscenario_id}/select",
    description="Set a dscenario as selected for the current user",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def select_dscenario(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).select_dscenario(dscenario_id)


@router.delete(
    "/dscenarios/{dscenario_id}",
    description="Delete a dscenario from ve_cat_dscenario",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def delete_dscenario(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).delete_dscenario(dscenario_id)


@router.get(
    "/dscenarios/{dscenario_id}/{object_type}",
    description="Get objects of a given type for a dscenario",
    response_model=GetListResponse,
    response_model_exclude_unset=True,
)
async def get_dscenario_objects(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    filter_fields: Optional[str] = Query(None, alias="filterFields", description="Additional filter fields"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).get_dscenario_objects(dscenario_id, object_type, filter_fields)


@router.post(
    "/dscenarios/{dscenario_id}/{object_type}",
    description="Insert objects (single or bulk) for a dscenario and object type",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def insert_dscenario_objects(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    objects: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(
        ...,
        title="Objects",
        description="Single object or list of objects to insert",
    ),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).insert_dscenario_objects(dscenario_id, object_type, objects)


@router.put(
    "/dscenarios/{dscenario_id}/{object_type}",
    description="Upsert objects (single or bulk) for a dscenario and object type",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def upsert_dscenario_objects(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    objects: Union[Dict[str, Any], List[Dict[str, Any]]] = Body(
        ...,
        title="Objects",
        description="Single object or list of objects to upsert; each must include the id field for this object type",
    ),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).upsert_dscenario_objects(dscenario_id, object_type, objects)


@router.get(
    "/dscenarios/{dscenario_id}/{object_type}/{object_id}",
    description="Get a single object of a given type for a dscenario",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def get_dscenario_object(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    object_id: str = Path(..., description="Object id"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).get_dscenario_object(dscenario_id, object_type, object_id)


@router.patch(
    "/dscenarios/{dscenario_id}/{object_type}/{object_id}",
    description="Update a single object for a dscenario and object type",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def update_dscenario_object(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    object_id: str = Path(..., description="Object id"),
    data: Dict[str, Any] = Body(..., title="Object", description="Fields to update"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).update_dscenario_object(dscenario_id, object_type, object_id, data)


@router.put(
    "/dscenarios/{dscenario_id}/{object_type}/{object_id}",
    description="Upsert a single object for a dscenario and object type",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def upsert_dscenario_object(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    object_id: str = Path(..., description="Object id"),
    data: Dict[str, Any] = Body(..., title="Object", description="Fields to upsert"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).upsert_dscenario_object(dscenario_id, object_type, object_id, data)


@router.delete(
    "/dscenarios/{dscenario_id}/{object_type}/{object_id}",
    description="Delete a single object for a dscenario and object type",
    response_model=DscenarioObjectResponse,
    response_model_exclude_unset=True,
)
async def delete_dscenario_object(
    commons: CommonsDep,
    dscenario_id: int = Path(..., description="Dscenario id"),
    object_type: DscenarioObjectType = Path(..., description="Dscenario object type"),
    object_id: str = Path(..., description="Object id"),
):
    ctx = get_service_context(commons)
    return await DscenarioService(ctx).delete_dscenario_object(dscenario_id, object_type, object_id)
