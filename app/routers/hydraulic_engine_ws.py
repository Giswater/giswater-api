"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/hydraulicengine/ws", tags=["Hydraulic Engine (WS)"])

@router.get("/getepafile")
async def get_epa_file():
    return {"message": "Fetched EPA file successfully"}

@router.post("/setepafile")
async def set_epa_file():
    return {"message": "EPA file attributes modified successfully"}

@router.put("/sethydrantreachability")
async def set_hydrant_reachability():
    return {"message": "Hydrant reachability set successfully"}

@router.put("/setreservoirvalue")
async def set_reservoir_value():
    return {"message": "Reservoir value updated successfully"}

@router.put("/setlinkvalue")
async def set_link_value():
    return {"message": "Link value updated successfully"}

@router.put("/setvalvevalue")
async def set_valve_value():
    return {"message": "Valve value modified successfully"}

@router.put("/settankvalue")
async def set_tank_value():
    return {"message": "Tank value modified successfully"}

@router.put("/setpumpvalue")
async def set_pump_value():
    return {"message": "Pump value modified successfully"}

@router.put("/setjunctionvalue")
async def set_junction_value():
    return {"message": "Junction value modified successfully"}

@router.put("/setpatternvalue")
async def set_pattern_value():
    return {"message": "Pattern value modified successfully"}

@router.put("/setcontrolsvalue")
async def set_controls_value():
    return {"message": "Controls value modified successfully"}

@router.post("/setsolveh")
async def set_solve_h():
    return {"message": "Pressure & flow simulation ran successfully"}

@router.post("/setsolveq")
async def set_solve_q():
    return {"message": "Water quality simulation ran successfully"}
