"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import json

from fastapi import APIRouter, Body, HTTPException, Path, Query
from typing import Any, Dict, List, Optional, Union
from pydantic import ValidationError

from ...utils.utils import (
    create_body_dict,
    create_log,
    execute_procedure,
    execute_sql_delete,
    execute_sql_insert,
    execute_sql_select,
    execute_sql_update,
    get_db_version,
    handle_procedure_result,
)
from ...models.basic.basic_models import GetListResponse
from ...models.epa.dscenario_models import (
    DscenarioCreateRequest,
    DscenarioFilterFieldsModel,
    DscenarioObjectResponse,
    DscenarioObjectType,
    get_dscenario_object_id_column,
    get_dscenario_table,
)
from ..basic.basic import get_list
from ...dependencies import CommonsDep

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
    log = create_log(__name__)

    parameters = {
        "name": payload.name,
        "descript": payload.descript or "",
        "parent": payload.parent,
        "type": payload.type,
        "active": "true" if payload.active else "false",
        "expl": str(payload.expl),
    }

    body = create_body_dict(
        project_epsg=None,
        extras={"parameters": parameters},
        cur_user=commons["user_id"],
        device=commons["device"],
        lang=commons["lang"],
    )

    result = await execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_create_dscenario_empty",
        body,
        schema=commons["schema"],
        user=commons["user_id"],
        api_version=commons["api_version"],
    )

    return handle_procedure_result(result)


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
    """Get list of mincuts by calling the generic get_list endpoint with tbl_mincut_manger table"""

    # Validate filterFields using the mincut-specific model
    if filter_fields:
        try:
            filter_fields_dict = json.loads(filter_fields)
            # Validate using MincutFilterFieldsModel
            DscenarioFilterFieldsModel(data=filter_fields_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid filterFields: {str(e)}") from e

    return await get_list(
        commons=commons,
        table_name="ve_cat_dscenario",
        coordinates=None,
        page_info=None,
        filter_fields=filter_fields,
    )


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
    log = create_log(__name__)

    table_name = "ve_cat_dscenario"
    where_data = {"dscenario_id": dscenario_id}

    status = await execute_sql_delete(
        log=log,
        db_manager=commons["db_manager"],
        table_name=table_name,
        where_data=where_data,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    if not status:
        raise HTTPException(status_code=404, detail="Dscenario not found")

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Dscenario deleted"},
        "version": {"db": db_version, "api": commons["api_version"]},
        "body": {
            "form": None,
            "feature": None,
            "data": None,
        },
    }


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
    """Get objects for a given dscenario and object type using the generic get_list endpoint."""

    merged_filters: Dict[str, Dict[str, Any]]

    if filter_fields:
        try:
            merged_filters = json.loads(filter_fields)
            if not isinstance(merged_filters, dict):
                raise ValueError("filterFields must be a JSON object")
        except (json.JSONDecodeError, ValueError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid filterFields: {str(e)}") from e
    else:
        merged_filters = {}

    merged_filters["dscenario_id"] = {"value": dscenario_id, "filterSign": "="}

    merged_filter_str = json.dumps(merged_filters)

    return await get_list(
        commons=commons,
        table_name=get_dscenario_table(object_type),
        coordinates=None,
        page_info=None,
        filter_fields=merged_filter_str,
    )


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
    log = create_log(__name__)

    table_name = get_dscenario_table(object_type)

    # Normalize to list and inject dscenario_id
    items_list = [objects] if isinstance(objects, dict) else objects

    all_rows: List[Dict[str, Any]] = []
    # TODO: Use bulk insert
    for obj in items_list:
        obj["dscenario_id"] = dscenario_id
        rows = await execute_sql_insert(
            log=log,
            db_manager=commons["db_manager"],
            table_name=table_name,
            data=obj,
            schema=commons["schema"],
            user=commons["user_id"],
        )
        all_rows.extend(rows)

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": f"Inserted {len(all_rows)} rows"},
        "version": {"db": db_version, "api": commons["api_version"]},
        "body": {
            "form": None,
            "feature": None,
            "data": {
                "items": all_rows,
                "count": len(all_rows),
            },
        },
    }


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
    object_id: Union[int, str] = Path(..., description="Object id"),
):
    log = create_log(__name__)
    table_name = get_dscenario_table(object_type)
    id_column = get_dscenario_object_id_column(object_type)

    rows = await execute_sql_select(
        log=log,
        db_manager=commons["db_manager"],
        table_name=table_name,
        where_clause="dscenario_id = %s AND {} = %s".format(id_column),
        parameters=(dscenario_id, object_id),
        schema=commons["schema"],
        user=commons["user_id"],
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Object not found")

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Object fetched"},
        "version": {"db": db_version, "api": commons["api_version"]},
        "body": {
            "form": None,
            "feature": None,
            "data": {
                "items": rows,
                "count": len(rows),
            },
        },
    }


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
    object_id: Union[int, str] = Path(..., description="Object id"),
    data: Dict[str, Any] = Body(..., title="Object", description="Fields to update"),
):
    log = create_log(__name__)
    table_name = get_dscenario_table(object_type)
    id_column = get_dscenario_object_id_column(object_type)

    update_data = dict(data)
    # Enforce dscenario and id in where; prevent overriding them in SET
    update_data.pop("dscenario_id", None)
    update_data.pop(id_column, None)

    if not update_data:
        raise HTTPException(status_code=400, detail="No updatable fields provided")

    where_data = {"dscenario_id": dscenario_id, id_column: object_id}

    rows = await execute_sql_update(
        log=log,
        db_manager=commons["db_manager"],
        table_name=table_name,
        data=update_data,
        where_data=where_data,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    if not rows:
        raise HTTPException(status_code=404, detail="Object not found")

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Object updated"},
        "version": {"db": db_version, "api": commons["api_version"]},
        "body": {
            "form": None,
            "feature": None,
            "data": {
                "items": rows,
                "count": len(rows),
            },
        },
    }


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
    object_id: Union[int, str] = Path(..., description="Object id"),
):
    log = create_log(__name__)
    table_name = get_dscenario_table(object_type)
    id_column = get_dscenario_object_id_column(object_type)

    where_data = {"dscenario_id": dscenario_id, id_column: object_id}

    status = await execute_sql_delete(
        log=log,
        db_manager=commons["db_manager"],
        table_name=table_name,
        where_data=where_data,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    if not status:
        raise HTTPException(status_code=404, detail="Object not found")

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Object deleted"},
        "version": {"db": db_version, "api": commons["api_version"]},
        "body": {
            "form": None,
            "feature": None,
            "data": None,
        },
    }
