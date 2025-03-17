"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/hydraulicengine/ud", tags=["Hydraulic Engine (UD)"])

@router.get("/getswmmfile")
async def get_swmm_file():
    return {"message": "Fetched SWMM file successfully"}

@router.post("/setswmmfile")
async def set_swmm_file():
    return {"message": "SWMM file attributes modified successfully"}

@router.put("/setnodevalue")
async def set_node_value():
    return {"message": "Node value modified successfully"}

@router.put("/setlinkvalue")
async def set_link_value():
    return {"message": "Link value modified successfully"}

@router.put("/setpumpvalue")
async def set_pump_value():
    return {"message": "Pump value modified successfully"}

@router.put("/setoverflowvalue")
async def set_overflow_value():
    return {"message": "Overflow value modified successfully"}

@router.post("/setswmmresult")
async def set_swmm_result():
    return {"message": "SWMM result set successfully"}

@router.post("/setsolvetime")
async def set_solve_time():
    return {"message": "Solve time set successfully"}

@router.put("/setcontrolvalue")
async def set_control_value():
    return {"message": "Control value modified successfully"}
