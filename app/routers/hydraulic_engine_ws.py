"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/hydraulicengine/ws", tags=["Hydraulic Engine (WS)"])

# region WS



# endregion

# region UD

@router.get("/getepafile")
async def get_epa_file():
    return {"message": "Fetched EPA file successfully"}

@router.post("/setepafile")
async def set_epa_file():
    return {"message": "EPA file attributes modified successfully"}

@router.post("/sethydrantreachability")
async def set_hydrant_reachability():
    return {"message": "Hydrant reachability set successfully"}

@router.get("/getswmmfile")
async def get_swmm_file():
    return {"message": "Fetched SWMM file successfully"}

@router.post("/setswmmfile")
async def set_swmm_file():
    return {"message": "SWMM file attributes modified successfully"}

@router.post("/setnodevalue")
async def set_node_value():
    return {"message": "Node value modified successfully"}

@router.post("/setlinkvalue")
async def set_link_value():
    return {"message": "Link value modified successfully"}

@router.post("/setpumpvalue")
async def set_pump_value():
    return {"message": "Pump value modified successfully"}

@router.post("/setoverflowvalue")
async def set_overflow_value():
    return {"message": "Overflow value modified successfully"}

@router.post("/setswmmresult")
async def set_swmm_result():
    return {"message": "SWMM result set successfully"}

@router.post("/setsolvetime")
async def set_solve_time():
    return {"message": "Solve time set successfully"}

@router.post("/setcontrolvalue")
async def set_control_value():
    return {"message": "Control value modified successfully"}

# endregion
