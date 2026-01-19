"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Query, Depends, Body, Request
from fastapi_keycloak import OIDCUser
from typing import List
from ...models.epa.hydraulic_engine_ud_models import (
    NodeValueUpdate,
    LinkValueUpdate,
    PumpValueUpdate,
    OverflowValueUpdate,
    ControlValueUpdate,
)
from ...utils.utils import create_log
from ...keycloak import get_current_user

router = APIRouter(prefix="/epa/ud", tags=["EPA - Hydraulic Engine (UD)"])


def get_network_scenario(
    network_scenario: str = Query(..., alias="networkScenario", description="SWMM network scenario"),
):
    return network_scenario


@router.get("/getswmmfile")
async def get_swmm_file(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {
        "message": "Fetched SWMM file successfully",
        "networkScenario": network_scenario,
    }


@router.post("/setswmmfile")
async def set_swmm_file(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {
        "message": "SWMM file attributes modified successfully",
        "networkScenario": network_scenario,
    }


@router.put("/setnodevalue")
async def set_node_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    update: NodeValueUpdate | List[NodeValueUpdate] = Body(..., title="Update", description="Update body"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Node value modified successfully", "networkScenario": network_scenario, "update": update}


@router.put("/setlinkvalue")
async def set_link_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    update: LinkValueUpdate | List[LinkValueUpdate] = Body(..., title="Update", description="Update body"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Link value modified successfully", "networkScenario": network_scenario, "update": update}


@router.put("/setpumpvalue")
async def set_pump_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    update: PumpValueUpdate | List[PumpValueUpdate] = Body(..., title="Update", description="Update body"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Pump value modified successfully", "networkScenario": network_scenario, "update": update}


@router.put("/setoverflowvalue")
async def set_overflow_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    update: OverflowValueUpdate | List[OverflowValueUpdate] = Body(..., title="Update", description="Update body"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Overflow value modified successfully", "networkScenario": network_scenario, "update": update}


@router.post("/setswmmresult")
async def set_swmm_result(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    result: dict = Body(..., title="Result", description="SWMM simulation result data"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "SWMM result set successfully", "networkScenario": network_scenario, "result": result}


@router.post("/setsolvetime")
async def set_solve_time(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    time: float = Body(..., title="Time", description="Time for the SWMM simulation to solve"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Solve time set successfully", "networkScenario": network_scenario, "time": time}


@router.put("/setcontrolvalue")
async def set_control_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user),
    network_scenario: str = Depends(get_network_scenario),
    update: ControlValueUpdate | List[ControlValueUpdate] = Body(..., title="Update", description="Update body"),
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Control value modified successfully", "networkScenario": network_scenario, "update": update}
