"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Body, Path
from typing import Optional

from ...models.util_models import CoordinatesModel, APIResponse
from ...models.om.mincut_models import (
    MincutPlanParams,
    MincutExecParams,
    ValveUnaccessResponse,
    MincutStartResponse,
    MincutDeleteResponse,
)
from ...utils.utils import create_body_dict, create_log, execute_procedure, create_api_response
from ...dependencies import CommonsDep

router = APIRouter(prefix="/om", tags=["OM - Mincut"])


@router.post(
    "/mincuts",
    description=(
        "This action should be used when an anomaly is detected in field that wasn't planified.\n"
        "In this case there is no mincut created, therefore a new one will be created."
    )
)
async def create_mincut(
    commons: CommonsDep,
    coordinates: CoordinatesModel = Body(
        ...,
        title="Coordinates",
        description="Coordinates on which the mincut will be created"
    ),
    workcatId: int = Body(
        ...,
        title="Workcat ID",
        description="ID of the work associated to the anomaly",
        examples=[1]
    ),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan of the mincut"),
    user: str = Body(..., title="User", description="User who is doing the action"),
) -> APIResponse:
    log = create_log(__name__)

    coordinates_dict = coordinates.model_dump()
    if plan:
        plan_dict = plan.model_dump(exclude_unset=True)
    else:
        plan_dict = {}

    print(plan_dict)
    # TODO: Add workcatId to the body
    # TODO: Use the plan fields
    body = create_body_dict(
        device=commons["device"],
        client_extras={"tiled": True},
        extras={"action": "mincutNetwork", "usePsectors": "False", "coordinates": coordinates_dict, "status": "check"},
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    # TODO: change response to a pydantic model
    if not result:
        return create_api_response("Error creating mincut", "Failed")

    if result.get("status") != "Accepted":
        return create_api_response("Error creating mincut", "Failed", result=result)

    return create_api_response("Created mincut successfully", "Accepted", result=result)


@router.patch(
    "/mincuts/{mincut_id}",
    description="This action should be used when a mincut is already created and it needs to be updated."
)
async def update_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to update", examples=[1]),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan parameters"),
    exec: Optional[MincutExecParams] = Body(None, title="Execution", description="Execution parameters"),
    user: str = Body(..., title="User", description="User who is doing the action"),
) -> APIResponse:
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
        client_extras={"tiled": True},
        feature={"featureType": "", "tableName": "om_mincut", "id": mincut_id},
        extras={"action": "mincutAccept", "mincutClass": 1, "status": "check",
                "mincutId": mincut_id, "usePsectors": "False",
                "fields": {
                    **plan_dict,
                    **exec_dict
                    }
                },
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    # TODO: change response to a pydantic model
    if not result:
        return create_api_response("Error updating mincut", "Failed")

    if result.get("status") != "Accepted":
        return create_api_response("Error updating mincut", "Failed", result=result)

    return create_api_response("Updated mincut successfully", "Accepted", result=result)


@router.post(
    "/mincuts/{mincut_id}/valve-unaccess",
    description=(
        "Recalculates the mincut when a defined one is invalid due to an inaccessible or inoperative valve. "
        "The system excludes the problematic valve and adjusts the cut polygon based on accessible valves."
    )
)
async def valve_unaccess(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut associated to the valve", examples=[1]),
    nodeId: int = Body(
        ...,
        title="Node ID",
        description="ID of the node where the unaccessible valve is located",
        examples=[1114]
    ),
    user: str = Body(..., title="User", description="User who is doing the action"),
) -> ValveUnaccessResponse | APIResponse:
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        client_extras={"tiled": True},
        extras={"action": "mincutValveUnaccess", "nodeId": nodeId, "mincutId": mincut_id, "usePsectors": "False"},
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    # TODO: change response to a pydantic model
    if not result:
        return create_api_response("Error recalculating mincut", "Failed")

    if result.get("status") != "Accepted":
        return create_api_response("Error recalculating mincut", "Failed", result=result)

    response = ValveUnaccessResponse(**result)
    return response


@router.post(
    "/mincuts/{mincut_id}/start",
    description=(
        "This action should be used when the mincut is ready to be executed. "
        "The system will start the mincut and the water supply will be interrupted on the affected zone."
    ),
    response_model=MincutStartResponse,
    response_model_exclude_unset=True
)
async def start_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(
        ...,
        title="Mincut ID",
        description="ID of the mincut to start",
        examples=[1]
    ),
    # TODO: check if these parameters are needed/wanted
    # arc_id: int = Body(
    #     ...,
    #     title="Arc ID",
    #     description="ID of the arc to start the mincut",
    #     examples=[113875]
    # ),
    # mincut_type: Literal["Demo", "Test", "Real"] = Body(
    #     ...,
    #     title="Mincut Type",
    #     description="Type of the mincut",
    #     examples=["Demo"]
    # ),
    # forecast_start: str = Body(
    #     ...,
    #     title="Forecast Start",
    #     description="Expected start of the mincut",
    #     examples=["2025-11-27 00:00:00"]
    # ),
    # forecast_end: str = Body(
    #     ...,
    #     title="Forecast End",
    #     description="Expected end of the mincut",
    #     examples=["2025-11-27 00:00:00"]
    # ),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        extras={
            "action": "mincutStart",
            "usePsectors": "False",
            "mincutId": mincut_id,
            # "arcId": arc_id,
            # "dialogMincutType": dialog_mincut_type,
            # "dialogForecastStart": forecast_start,
            # "dialogForecastEnd": forecast_end
        },
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    return result


@router.post(
    "/mincuts/{mincut_id}/end",
    description=(
        "This action should be used when the mincut has been executed and the water supply is restored. "
        "The system will end the mincut and the affected zone will be restored."
    )
)
async def end_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to end", examples=[1]),
):
    log = create_log(__name__)  # noqa: F841
    # TODO: Add call to database funtion
    return create_api_response("Mincut ended successfully", "Accepted")


@router.post(
    "/mincuts/{mincut_id}/repair",
    description=(
        "Accepts the mincut but performs the repair without interrupting the water supply. "
        "A silent mincut is generated, allowing work on the network without affecting users."
    )
)
async def repair_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to repair", examples=[1]),
):
    log = create_log(__name__)  # noqa: F841
    # TODO: Add call to database funtion
    return create_api_response("Mincut repaired successfully", "Accepted")


@router.post(
    "/mincuts/{mincut_id}/cancel",
    description=(
        "Cancels the mincut when the repair is not feasible, "
        "nullifying the planned cut while keeping the issue recorded for future resolution. "
        "This ensures proper outage management and prevents data loss."
    )
)
async def cancel_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to cancel", examples=[1]),
):
    log = create_log(__name__)  # noqa: F841
    # TODO: Add call to database funtion
    return create_api_response("Mincut canceled successfully", "Accepted")


@router.delete(
    "/mincuts/{mincut_id}",
    description="Deletes the mincut from the system. This action should be used when the mincut is no longer needed.",
    response_model=MincutDeleteResponse,
    response_model_exclude_unset=True
)
async def delete_mincut(
    commons: CommonsDep,
    mincut_id: int = Path(..., title="Mincut ID", description="ID of the mincut to delete", examples=[1]),
):
    log = create_log(__name__)

    body = create_body_dict(
        device=commons["device"],
        extras={
            "action": "mincutDelete",
            "mincutId": mincut_id
        },
        cur_user=commons["user_id"]
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_setmincut",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"]
    )
    return result
