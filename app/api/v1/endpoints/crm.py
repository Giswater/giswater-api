"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Body
from typing import Union, List

from app.schemas.crm.crm_models import HydrometerCreate, HydrometerUpdate, HydrometerResponse
from app.api.deps import CommonsDep
from app.api.http_errors import map_service_error
from app.services.context import service_context_from_commons
from app.services.crm_service import CrmService

router = APIRouter(prefix="/crm", tags=["CRM"])


@router.post(
    "/hydrometers",
    description="Insert hydrometers (single or bulk)",
    response_model=HydrometerResponse,
    response_model_exclude_unset=True,
)
async def insert_hydrometers(
    commons: CommonsDep,
    hydrometers: Union[HydrometerCreate, List[HydrometerCreate]] = Body(
        ..., title="Hydrometers", description="Single hydrometer or list of hydrometers to insert"
    ),
):
    """Insert one or multiple hydrometers"""
    try:
        ctx = service_context_from_commons(commons)
        hydrometers_list = hydrometers if isinstance(hydrometers, list) else [hydrometers]
        return await CrmService(ctx).insert_hydrometers(hydrometers_list)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.patch(
    "/hydrometers/{code}",
    description="Update a single hydrometer by code",
    response_model=HydrometerResponse,
    response_model_exclude_unset=True,
)
async def update_hydrometer(
    commons: CommonsDep,
    code: str,
    hydrometer: HydrometerUpdate = Body(
        ..., title="Hydrometer", description="Hydrometer data to update (partial data allowed)"
    ),
):
    """Update a single hydrometer identified by code"""
    try:
        ctx = service_context_from_commons(commons)
        return await CrmService(ctx).update_hydrometer(code, hydrometer)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.patch(
    "/hydrometers",
    description="Update multiple hydrometers in bulk",
    response_model=HydrometerResponse,
    response_model_exclude_unset=True,
)
async def update_hydrometers_bulk(
    commons: CommonsDep,
    hydrometers: List[HydrometerUpdate] = Body(
        ..., title="Hydrometers", description="List of hydrometers to update (partial data allowed)"
    ),
):
    """Update multiple hydrometers. Each must include 'code' as identifier"""
    try:
        ctx = service_context_from_commons(commons)
        return await CrmService(ctx).update_hydrometers_bulk(hydrometers)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.delete(
    "/hydrometers/{code}",
    description="Delete a single hydrometer by code",
    response_model=HydrometerResponse,
    response_model_exclude_unset=True,
)
async def delete_hydrometer(commons: CommonsDep, code: str):
    """Delete a single hydrometer identified by code"""
    try:
        ctx = service_context_from_commons(commons)
        return await CrmService(ctx).delete_hydrometer(code)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.delete(
    "/hydrometers",
    description="Delete multiple hydrometers in bulk",
    response_model=HydrometerResponse,
    response_model_exclude_unset=True,
)
async def delete_hydrometers_bulk(
    commons: CommonsDep,
    codes: List[str] = Body(..., title="Codes", description="List of hydrometer codes to delete"),
):
    """Delete multiple hydrometers by their codes"""
    try:
        ctx = service_context_from_commons(commons)
        return await CrmService(ctx).delete_hydrometers_bulk(codes)
    except Exception as exc:
        raise map_service_error(exc) from exc


@router.put(
    "/hydrometers",
    description="Replace all hydrometers. Deletes all existing hydrometers and inserts the provided ones.",
    response_model=HydrometerResponse,
    response_model_exclude_unset=True,
)
async def replace_all_hydrometers(
    commons: CommonsDep,
    hydrometers: List[HydrometerCreate] = Body(
        ...,
        title="Hydrometers",
        description="Complete list of hydrometers to replace existing ones (can be empty array)",
    ),
):
    """
    Full sync mode: Replace all hydrometers with the provided list.
    This will DELETE all existing hydrometers and INSERT only the ones provided.
    Works consistently whether there are 0 or 1000+ existing hydrometers.
    """
    try:
        ctx = service_context_from_commons(commons)
        return await CrmService(ctx).replace_all_hydrometers(hydrometers)
    except Exception as exc:
        raise map_service_error(exc) from exc
