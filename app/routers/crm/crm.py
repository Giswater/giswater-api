"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Depends, Body, Request
from fastapi_keycloak import OIDCUser
from typing import Union, List
from ...utils.utils import create_body_dict, execute_procedure, create_log
from ...models.util_models import GwErrorResponse
from ...models.crm.crm_models import (
    HydrometerCreate,
    HydrometerUpdate,
    HydrometerResponse
)
from ...dependencies import get_schema
from ...keycloak import get_current_user

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.post(
    "/hydrometers",
    description="Insert hydrometers (single or bulk)",
    response_model=Union[HydrometerResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def insert_hydrometers(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
    hydrometers: Union[HydrometerCreate, List[HydrometerCreate]] = Body(
        ...,
        title="Hydrometers",
        description="Single hydrometer or list of hydrometers to insert"
    ),
):
    """Insert one or multiple hydrometers"""
    log = create_log(__name__)
    db_manager = request.app.state.db_manager
    user_id = current_user.preferred_username

    # Convert single object to list for uniform processing
    hydrometers_list = hydrometers if isinstance(hydrometers, list) else [hydrometers]

    # Convert to dict and handle date serialization
    hydrometers_data = [h.model_dump(mode='json', exclude_unset=True) for h in hydrometers_list]

    body = create_body_dict(
        extras={
            "action": "INSERT",
            "hydrometers": hydrometers_data
        }
    )

    result = execute_procedure(log, db_manager, "gw_fct_set_hydrometers", body, schema=schema, api_version=request.app.version)
    return result


@router.patch(
    "/hydrometers/{code}",
    description="Update a single hydrometer by code",
    response_model=Union[HydrometerResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def update_hydrometer(
    request: Request,
    code: str,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
    hydrometer: HydrometerUpdate = Body(
        ...,
        title="Hydrometer",
        description="Hydrometer data to update (partial data allowed)"
    ),
):
    """Update a single hydrometer identified by code"""
    log = create_log(__name__)
    db_manager = request.app.state.db_manager
    user_id = current_user.preferred_username

    # Override the code from path parameter
    hydrometer_dict = hydrometer.model_dump(mode='json', exclude_unset=True)
    hydrometer_dict['code'] = code

    body = create_body_dict(
        extras={
            "action": "UPDATE",
            "hydrometers": [hydrometer_dict]
        }
    )

    result = execute_procedure(log, db_manager, "gw_fct_set_hydrometers", body, schema=schema, api_version=request.app.version)
    return result


@router.patch(
    "/hydrometers",
    description="Update multiple hydrometers in bulk",
    response_model=Union[HydrometerResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def update_hydrometers_bulk(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
    hydrometers: List[HydrometerUpdate] = Body(
        ...,
        title="Hydrometers",
        description="List of hydrometers to update (partial data allowed)"
    ),
):
    """Update multiple hydrometers. Each must include 'code' as identifier"""
    log = create_log(__name__)
    db_manager = request.app.state.db_manager
    user_id = current_user.preferred_username

    hydrometers_data = [h.model_dump(mode='json', exclude_unset=True) for h in hydrometers]

    body = create_body_dict(
        extras={
            "action": "UPDATE",
            "hydrometers": hydrometers_data
        }
    )

    result = execute_procedure(log, db_manager, "gw_fct_set_hydrometers", body, schema=schema, api_version=request.app.version)
    return result


@router.delete(
    "/hydrometers/{code}",
    description="Delete a single hydrometer by code",
    response_model=Union[HydrometerResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def delete_hydrometer(
    request: Request,
    code: str,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
):
    """Delete a single hydrometer identified by code"""
    log = create_log(__name__)
    db_manager = request.app.state.db_manager
    user_id = current_user.preferred_username

    body = create_body_dict(
        extras={
            "action": "DELETE",
            "hydrometers": [{"code": code}]
        }
    )

    result = execute_procedure(log, db_manager, "gw_fct_set_hydrometers", body, schema=schema, api_version=request.app.version)
    return result


@router.delete(
    "/hydrometers",
    description="Delete multiple hydrometers in bulk",
    response_model=Union[HydrometerResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def delete_hydrometers_bulk(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
    codes: List[str] = Body(
        ...,
        title="Codes",
        description="List of hydrometer codes to delete"
    ),
):
    """Delete multiple hydrometers by their codes"""
    log = create_log(__name__)
    db_manager = request.app.state.db_manager
    user_id = current_user.preferred_username

    hydrometers_data = [{"code": code} for code in codes]

    body = create_body_dict(
        extras={
            "action": "DELETE",
            "hydrometers": hydrometers_data
        }
    )

    result = execute_procedure(log, db_manager, "gw_fct_set_hydrometers", body, schema=schema, api_version=request.app.version)
    return result


@router.put(
    "/hydrometers",
    description="Replace all hydrometers. Deletes all existing hydrometers and inserts the provided ones.",
    response_model=Union[HydrometerResponse, GwErrorResponse],
    response_model_exclude_unset=True
)
async def replace_all_hydrometers(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
    hydrometers: List[HydrometerCreate] = Body(
        ...,
        title="Hydrometers",
        description="Complete list of hydrometers to replace existing ones (can be empty array)"
    ),
):
    """
    Full sync mode: Replace all hydrometers with the provided list.
    This will DELETE all existing hydrometers and INSERT only the ones provided.
    Works consistently whether there are 0 or 1000+ existing hydrometers.
    """
    log = create_log(__name__)
    db_manager = request.app.state.db_manager
    user_id = current_user.preferred_username

    hydrometers_data = [h.model_dump(mode='json', exclude_unset=True) for h in hydrometers]

    body = create_body_dict(
        extras={
            "action": "REPLACE",
            "hydrometers": hydrometers_data
        }
    )

    result = execute_procedure(log, db_manager, "gw_fct_set_hydrometers", body, schema=schema, api_version=request.app.version)
    return result
