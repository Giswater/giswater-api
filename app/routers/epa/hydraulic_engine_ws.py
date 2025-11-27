"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query, Depends, Body, Request
from fastapi_keycloak import OIDCUser
from typing import List

from ...models.epa.hydraulic_engine_ws_models import (
    HydrantReachabilityUpdate,
    ReservoirValueUpdate,
    LinkValueUpdate,
    ValveValueUpdate,
    TankValueUpdate,
    PumpValueUpdate,
    JunctionValueUpdate,
    PatternValueUpdate,
    ControlValueUpdate
)
from ...utils.utils import create_log
from ...keycloak import get_current_user

router = APIRouter(prefix="/epa/ws", tags=["EPA - Hydraulic Engine (WS)"])


def get_network_scenario(
    networkScenario: str = Query(..., description="EPANET network scenario")
):
    return networkScenario


@router.get("/getepafile")
async def get_epa_file(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario)
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Fetched EPA file successfully"}


@router.post("/setepafile")
async def set_epa_file(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario)
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "EPA file attributes modified successfully"}


@router.put("/sethydrantreachability")
async def set_hydrant_reachability(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: HydrantReachabilityUpdate | List[HydrantReachabilityUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Hydrant reachability set successfully"}


@router.put("/setreservoirvalue")
async def set_reservoir_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: ReservoirValueUpdate | List[ReservoirValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Reservoir value updated successfully"}


@router.put("/setlinkvalue")
async def set_link_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: LinkValueUpdate | List[LinkValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Link value updated successfully"}


@router.put("/setvalvevalue")
async def set_valve_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: ValveValueUpdate | List[ValveValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Valve value modified successfully"}


@router.put("/settankvalue")
async def set_tank_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: TankValueUpdate | List[TankValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Tank value modified successfully"}


@router.put("/setpumpvalue")
async def set_pump_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: PumpValueUpdate | List[PumpValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Pump value modified successfully"}


@router.put("/setjunctionvalue")
async def set_junction_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: JunctionValueUpdate | List[JunctionValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Junction value modified successfully"}


@router.put("/setpatternvalue")
async def set_pattern_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: PatternValueUpdate | List[PatternValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Pattern value modified successfully"}


@router.put("/setcontrolsvalue")
async def set_controls_value(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario),
    update: ControlValueUpdate | List[ControlValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Controls value modified successfully"}


@router.post("/setsolveh")
async def set_solve_h(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario)
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Pressure & flow simulation ran successfully"}


@router.post("/setsolveq")
async def set_solve_q(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    networkScenario: str = Depends(get_network_scenario)
):
    log = create_log(__name__)  # noqa: F841
    db_manager = request.app.state.db_manager  # noqa: F841
    user_id = current_user.preferred_username  # noqa: F841
    return {"message": "Water quality simulation ran successfully"}
