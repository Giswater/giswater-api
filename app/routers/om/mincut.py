"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

import json
from fastapi import APIRouter, Body, Path, Query, HTTPException
from typing import Optional
from pydantic import ValidationError

from ...models.util_models import CoordinatesModel
from ...models.om.mincut_models import (
    MINCUT_CAUSE_VALUES,
    MincutPlanParams,
    MincutExecParams,
    MincutCreateResponse,
    MincutUpdateResponse,
    MincutToggleValveUnaccessResponse,
    MincutToggleValveStatusResponse,
    MincutStartResponse,
    MincutDeleteResponse,
    MincutFilterFieldsModel,
    MincutValveFilterFieldsModel,
    MincutCancelResponse,
    MincutEndResponse,
    MincutDialogResponse,
)
from ...models.basic.basic_models import GetListResponse
from ...utils.utils import create_body_dict, create_log, execute_procedure, handle_procedure_result
from ...dependencies import CommonsDep
from ..basic.basic import get_list

router = APIRouter(prefix="/om", tags=["OM - Mincut"])


@router.get(
    "/mincuts",
    description="Returns a list of mincuts",
    response_model=GetListResponse,
    response_model_exclude_unset=True,
)
async def get_mincuts(
    commons: CommonsDep,
    filter_fields: Optional[str] = Query(None, alias="filterFields", description="Filter fields"),
):
    """Get list of mincuts by calling the generic get_list endpoint with tbl_mincut_manger table"""

    # Validate filterFields using the mincut-specific model
    if filter_fields:
        try:
            filter_fields_dict = json.loads(filter_fields)
            # Validate using MincutFilterFieldsModel
            MincutFilterFieldsModel(data=filter_fields_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid filterFields: {str(e)}") from e

    return await get_list(
        commons=commons,
        table_name="tbl_mincut_manager",
        coordinates=None,
        page_info=None,
        filter_fields=filter_fields,
    )


@router.get(
    "/mincuts/{mincut_id}",
    description="Returns the dialog data of a mincut",
    response_model=MincutDialogResponse,
    response_model_exclude_unset=True,
)
async def get_mincut_dialog(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to fetch", examples=[1]),
):
    log = create_log(__name__)

    body = create_body_dict(device=commons["device"], extras={"mincutId": mincut_id}, cur_user=commons["user_id"])

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.post(
    "/mincuts",
    description=(
        "This action should be used when an anomaly is detected in field that wasn't planified.\n"
        "In this case there is no mincut created, therefore a new one will be created."
    ),
    response_model=MincutCreateResponse,
    response_model_exclude_unset=True,
)
async def create_mincut(
    commons: CommonsDep,
    coordinates: CoordinatesModel = Body(
        ..., title="Coordinates", description="Coordinates on which the mincut will be created"
    ),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan of the mincut"),
    use_psectors: bool = Body(False, title="Use Psectors", description="Whether to use the planified network or not"),
):
    log = create_log(__name__)

    coordinates_dict = coordinates.model_dump()
    if plan:
        plan_dict = plan.model_dump(exclude_unset=True)
    else:
        plan_dict = {}

    if plan_dict.get("anl_cause"):
        plan_dict["anl_cause"] = MINCUT_CAUSE_VALUES.get(plan_dict["anl_cause"])

    extras = {
        "action": "mincutNetwork",
        "usePsectors": use_psectors,
        "coordinates": coordinates_dict,
        "status": "check",
        **plan_dict,
    }
    body = create_body_dict(
        device=commons["device"], client_extras={"tiled": True}, extras=extras, cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )

    return handle_procedure_result(result)


@router.patch(
    "/mincuts/{mincut_id}",
    description="This action should be used when a mincut is already created and it needs to be updated.",
    response_model=MincutUpdateResponse,
    response_model_exclude_unset=True,
)
async def update_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to update", examples=[1]),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan parameters"),
    exec: Optional[MincutExecParams] = Body(None, title="Execution", description="Execution parameters"),
    use_psectors: bool = Body(False, title="Use Psectors", description="Whether to use the planified network or not"),
):
    log = create_log(__name__)

    if plan:
        plan_dict = plan.model_dump(exclude_unset=True)
    else:
        plan_dict = {}

    if exec:
        exec_dict = exec.model_dump(exclude_unset=True)
    else:
        exec_dict = {}

    body = create_body_dict(
        device=commons["device"],
        feature={"featureType": "", "tableName": "om_mincut", "id": mincut_id},
        extras={
            "action": "mincutAccept",
            "mincutClass": 1,
            "status": "check",
            "mincutId": mincut_id,
            "usePsectors": use_psectors,
            "fields": {**plan_dict, **exec_dict},
        },
        cur_user=commons["user_id"],
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )

    return handle_procedure_result(result)


@router.get(
    "/mincuts/{mincut_id}/valves",
    description=("Gets the list of valves associated to a mincut."),
    response_model=GetListResponse,
    response_model_exclude_unset=True,
)
async def get_valves(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut associated to the valve", examples=[1]),
    filter_fields: Optional[str] = Query(None, alias="filterFields", description="Filter fields"),
):
    # Validate filterFields using the mincut-specific model
    if filter_fields:
        try:
            filter_fields_dict = json.loads(filter_fields)
            filter_fields_dict["result_id"] = mincut_id
            # Validate using MincutValveFilterFieldsModel
            MincutValveFilterFieldsModel(data=filter_fields_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid filterFields: {str(e)}") from e

    return await get_list(
        commons=commons,
        table_name="v_om_mincut_valve",
        coordinates=None,
        page_info=None,
        filter_fields=filter_fields,
    )


@router.post(
    "/mincuts/{mincut_id}/valves/{valve_id}/toggle-unaccess",
    description=(
        "Toggles the unaccess status of a valve associated to a mincut."
        "Also recalculates the mincut with the new status of the valve."
    ),
    response_model=MincutToggleValveUnaccessResponse,
    response_model_exclude_unset=True,
)
async def valve_unaccess(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut associated to the valve", examples=[1]),
    valve_id: int = Path(..., title="Node ID", description="ID of the valve to toggle unaccessible", examples=[1114]),
    use_psectors: bool = Body(False, title="Use Psectors", description="Whether to use the planified network or not"),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        extras={
            "action": "mincutValveUnaccess",
            "nodeId": valve_id,
            "mincutId": mincut_id,
            "usePsectors": use_psectors,
        },
        cur_user=commons["user_id"],
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.post(
    "/mincuts/{mincut_id}/valves/{valve_id}/toggle-status",
    description=("Updates the status of a valve associated to a mincut."),
    response_model=MincutToggleValveStatusResponse,
    response_model_exclude_unset=True,
)
async def valve_toggle_status(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut associated to the valve", examples=[1]),
    valve_id: int = Path(..., title="Valve ID", description="ID of the valve to update", examples=[1114]),
    use_psectors: bool = Body(False, title="Use Psectors", description="Whether to use the planified network or not"),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        extras={
            "action": "mincutChangeValveStatus",
            "nodeId": valve_id,
            "mincutId": mincut_id,
            "usePsectors": use_psectors,
        },
        cur_user=commons["user_id"],
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.post(
    "/mincuts/{mincut_id}/start",
    description=(
        "This action should be used when the mincut is ready to be executed. "
        "The system will start the mincut and the water supply will be interrupted on the affected zone."
    ),
    response_model=MincutStartResponse,
    response_model_exclude_unset=True,
)
async def start_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to start", examples=[1]),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan parameters"),
    use_psectors: bool = Body(False, title="Use Psectors", description="Whether to use the planified network or not"),
):
    log = create_log(__name__)

    if plan:
        plan_dict = plan.model_dump(exclude_unset=True)
    else:
        plan_dict = {}

    body = create_body_dict(
        device=commons["device"],
        extras={"action": "mincutStart", "usePsectors": use_psectors, "mincutId": mincut_id, **plan_dict},
        cur_user=commons["user_id"],
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.post(
    "/mincuts/{mincut_id}/end",
    description=(
        "This action should be used when the mincut has been executed and the water supply is restored. "
        "The system will end the mincut and the affected zone will be restored."
    ),
    response_model=MincutEndResponse,
    response_model_exclude_unset=True,
)
async def end_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to end", examples=[1]),
    shutoff_required: Optional[bool] = Body(
        True,
        title="Shutoff Required",
        description=("Whether the mincut required shutting off the water supply to consumers"),
        examples=[True],
    ),
    exec: Optional[MincutExecParams] = Body(None, title="Execution", description="Execution parameters"),
    use_psectors: bool = Body(False, title="Use Psectors", description="Whether to use the planified network or not"),
):
    log = create_log(__name__)

    if exec:
        exec_dict = exec.model_dump(exclude_unset=True)
    else:
        exec_dict = {}

    body = create_body_dict(
        device=commons["device"],
        extras={
            "action": "mincutEnd",
            "mincutId": mincut_id,
            "shutoffRequired": shutoff_required,
            "usePsectors": use_psectors,
            **exec_dict,
        },
        cur_user=commons["user_id"],
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.post(
    "/mincuts/{mincut_id}/cancel",
    description=(
        "Cancels the mincut when the repair is not feasible, "
        "nullifying the planned cut while keeping the issue recorded for future resolution. "
        "This ensures proper outage management and prevents data loss."
    ),
    response_model=MincutCancelResponse,
    response_model_exclude_unset=True,
)
async def cancel_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to cancel", examples=[1]),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"], extras={"action": "mincutCancel", "mincutId": mincut_id}, cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)


@router.delete(
    "/mincuts/{mincut_id}",
    description="Deletes the mincut from the system. This action should be used when the mincut is no longer needed.",
    response_model=MincutDeleteResponse,
    response_model_exclude_unset=True,
)
async def delete_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to delete", examples=[1]),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"], extras={"action": "mincutDelete", "mincutId": mincut_id}, cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)
