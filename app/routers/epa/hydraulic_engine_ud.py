"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query, Depends, Body
from typing import List
from ...models.epa.hydraulic_engine_ud_models import (
    NodeValueUpdate,
    LinkValueUpdate,
    PumpValueUpdate,
    OverflowValueUpdate,
    ControlValueUpdate
)

router = APIRouter(prefix="/epa/ud", tags=["EPA - Hydraulic Engine (UD)"])


def get_network_scenario(
    networkScenario: str = Query(..., description="SWMM network scenario")
):
    return networkScenario


@router.get("/getswmmfile")
async def get_swmm_file(
    networkScenario: str = Depends(get_network_scenario)
):
    return {
        "message": "Fetched SWMM file successfully",
        "networkScenario": networkScenario
    }


@router.post("/setswmmfile")
async def set_swmm_file(
    networkScenario: str = Depends(get_network_scenario)
):
    return {
        "message": "SWMM file attributes modified successfully",
        "networkScenario": networkScenario
    }


@router.put("/setnodevalue")
async def set_node_value(
    networkScenario: str = Depends(get_network_scenario),
    update: NodeValueUpdate | List[NodeValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {
        "message": "Node value modified successfully",
        "networkScenario": networkScenario,
        "update": update
    }


@router.put("/setlinkvalue")
async def set_link_value(
    networkScenario: str = Depends(get_network_scenario),
    update: LinkValueUpdate | List[LinkValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {
        "message": "Link value modified successfully",
        "networkScenario": networkScenario,
        "update": update
    }


@router.put("/setpumpvalue")
async def set_pump_value(
    networkScenario: str = Depends(get_network_scenario),
    update: PumpValueUpdate | List[PumpValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {
        "message": "Pump value modified successfully",
        "networkScenario": networkScenario,
        "update": update
    }


@router.put("/setoverflowvalue")
async def set_overflow_value(
    networkScenario: str = Depends(get_network_scenario),
    update: OverflowValueUpdate | List[OverflowValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {
        "message": "Overflow value modified successfully",
        "networkScenario": networkScenario,
        "update": update
    }


@router.post("/setswmmresult")
async def set_swmm_result(
    networkScenario: str = Depends(get_network_scenario),
    result: dict = Body(
        ...,
        title="Result",
        description="SWMM simulation result data"
    )
):
    return {
        "message": "SWMM result set successfully",
        "networkScenario": networkScenario,
        "result": result
    }


@router.post("/setsolvetime")
async def set_solve_time(
    networkScenario: str = Depends(get_network_scenario),
    time: float = Body(
        ...,
        title="Time",
        description="Time for the SWMM simulation to solve"
    )
):
    return {
        "message": "Solve time set successfully",
        "networkScenario": networkScenario,
        "time": time
    }


@router.put("/setcontrolvalue")
async def set_control_value(
    networkScenario: str = Depends(get_network_scenario),
    update: ControlValueUpdate | List[ControlValueUpdate] = Body(
        ...,
        title="Update",
        description="Update body"
    )
):
    return {
        "message": "Control value modified successfully",
        "networkScenario": networkScenario,
        "update": update
    }
