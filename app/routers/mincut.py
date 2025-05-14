"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Body, Query, Depends
from typing import Optional

from ..models.util_models import Coordinates
from ..models.mincut_models import MincutPlanParams, MincutExecParams
from ..utils import create_body_dict, create_log, execute_procedure, create_api_response
from ..dependencies import get_schema

router = APIRouter(prefix="/mincut", tags=["Mincut"])

@router.post("/newmincut", description="This action should be used when an anomaly is detected in field that wasn't planified.\nIn this case there is no mincut created, therefore a new one will be created.")
async def new_mincut(
    schema: str = Depends(get_schema),
    coordinates: Coordinates = Body(..., title="Coordinates", description="Coordinates on which the mincut will be created"),
    workcatId: int = Body(..., title="Workcat ID", description="ID of the work associated to the anomaly", examples=[1]),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan of the mincut"),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    log = create_log(__name__)

    coordinates_dict = coordinates.model_dump()
    if plan:
        plan_dict = plan.model_dump(exclude_unset=True)
    else:
        plan_dict = {}

    body = create_body_dict(
        client_extras={"tiled": True},
        extras={"action": "mincutNetwork", "usePsectors": "False", "coordinates": coordinates_dict, "status": "check"}
    )

    result = execute_procedure(log, "gw_fct_setmincut", body, schema=schema)
    if not result:
        return create_api_response("Error creating mincut", "Failed")

    if result.get("status") != "Accepted":
        return create_api_response("Error creating mincut", "Failed", result=result)

    return create_api_response("Created mincut successfully", "Accepted", result=result)

@router.patch("/updatemincut", description="This action should be used when a mincut is already created and it needs to be updated.")
async def update_mincut(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut to update", examples=[1]),
    plan: Optional[MincutPlanParams] = Body(None, title="Plan", description="Plan parameters"),
    exec: Optional[MincutExecParams] = Body(None, title="Execution", description="Execution parameters"),
    user: str = Body(..., title="User", description="User who is doing the action"),
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
        client_extras={"tiled": True},
        feature={"featureType": "", "tableName": "om_mincut", "id": mincutId},
        extras={"action": "mincutAccept", "mincutClass": 1, "status": "check", "mincutId": mincutId, "usePsectors": "False",
                "fields": {
                    **plan_dict,
                    **exec_dict
                    }
                }
    )

    result = execute_procedure(log, "gw_fct_setmincut", body, schema=schema)
    if not result:
        return create_api_response("Error updating mincut", "Failed")

    if result.get("status") != "Accepted":
        return create_api_response("Error updating mincut", "Failed", result=result)

    return create_api_response("Updated mincut successfully", "Accepted", result=result)

@router.put(
        "/valveunaccess",
        description=("Recalculates the mincut when a defined one is invalid due to an inaccessible or inoperative valve. "
                     "The system excludes the problematic valve and adjusts the cut polygon based on accessible valves.")
    )
async def valve_unaccess(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut associated to the valve", examples=[1]),
    nodeId: int = Body(..., title="Node ID", description="ID of the node where the unaccessible valve is located", examples=[1001]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return create_api_response("Valve unaccessed successfully", "Accepted")

@router.put(
    "/startmincut",
    description="This action should be used when the mincut is ready to be executed. The system will start the mincut and the water supply will be interrupted on the affected zone."
)
async def start_mincut(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut to start", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return create_api_response("Mincut started successfully", "Accepted")

@router.put(
    "/endmincut",
    description=("This action should be used when the mincut has been executed and the water supply is restored. "
                 "The system will end the mincut and the affected zone will be restored.")
)
async def end_mincut(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut to end", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return create_api_response("Mincut ended successfully", "Accepted")

@router.put(
    "/repairmincut",
    description=("Accepts the mincut but performs the repair without interrupting the water supply. "
                 "A silent mincut is generated, allowing work on the network without affecting users.")
)
async def repair_mincut(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut to repair", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return create_api_response("Mincut repaired successfully", "Accepted")

@router.put(
    "/cancelmincut",
    description=("Cancels the mincut when the repair is not feasible, nullifying the planned cut while keeping the issue recorded for future resolution. "
                 "This ensures proper outage management and prevents data loss.")
)
async def cancel_mincut(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut to cancel", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return create_api_response("Mincut canceled successfully", "Accepted")

@router.delete(
    "/deletemincut",
    description="Deletes the mincut from the system. This action should be used when the mincut is no longer needed."
)
async def delete_mincut(
    schema: str = Depends(get_schema),
    mincutId: int = Query(..., title="Mincut ID", description="ID of the mincut to delete", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return create_api_response("Mincut deleted successfully", "Accepted")
