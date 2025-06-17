"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query, Depends, Body
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

router = APIRouter(prefix="/epa/ws", tags=["EPA - Hydraulic Engine (WS)"])


def get_network_scenario(
    networkScenario: str = Query(..., description="EPANET network scenario")
):
    return networkScenario


@router.get("/getepafile")
async def get_epa_file(
    networkScenario: str = Depends(get_network_scenario)
):
    return {"message": "Fetched EPA file successfully"}


@router.post("/setepafile")
async def set_epa_file(
    networkScenario: str = Depends(get_network_scenario)
):
    return {"message": "EPA file attributes modified successfully"}


@router.put("/sethydrantreachability")
async def set_hydrant_reachability(
    networkScenario: str = Depends(get_network_scenario),
    update: HydrantReachabilityUpdate | List[HydrantReachabilityUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Hydrant reachability set successfully"}


@router.put("/setreservoirvalue")
async def set_reservoir_value(
    networkScenario: str = Depends(get_network_scenario),
    update: ReservoirValueUpdate | List[ReservoirValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Reservoir value updated successfully"}


@router.put("/setlinkvalue")
async def set_link_value(
    networkScenario: str = Depends(get_network_scenario),
    update: LinkValueUpdate | List[LinkValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Link value updated successfully"}


@router.put("/setvalvevalue")
async def set_valve_value(
    networkScenario: str = Depends(get_network_scenario),
    update: ValveValueUpdate | List[ValveValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Valve value modified successfully"}


@router.put("/settankvalue")
async def set_tank_value(
    networkScenario: str = Depends(get_network_scenario),
    update: TankValueUpdate | List[TankValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Tank value modified successfully"}


@router.put("/setpumpvalue")
async def set_pump_value(
    networkScenario: str = Depends(get_network_scenario),
    update: PumpValueUpdate | List[PumpValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Pump value modified successfully"}


@router.put("/setjunctionvalue")
async def set_junction_value(
    networkScenario: str = Depends(get_network_scenario),
    update: JunctionValueUpdate | List[JunctionValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Junction value modified successfully"}


@router.put("/setpatternvalue")
async def set_pattern_value(
    networkScenario: str = Depends(get_network_scenario),
    update: PatternValueUpdate | List[PatternValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Pattern value modified successfully"}


@router.put("/setcontrolsvalue")
async def set_controls_value(
    networkScenario: str = Depends(get_network_scenario),
    update: ControlValueUpdate | List[ControlValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {"message": "Controls value modified successfully"}


@router.post("/setsolveh")
async def set_solve_h(
    networkScenario: str = Depends(get_network_scenario)
):
    return {"message": "Pressure & flow simulation ran successfully"}


@router.post("/setsolveq")
async def set_solve_q(
    networkScenario: str = Depends(get_network_scenario)
):
    return {"message": "Water quality simulation ran successfully"}
