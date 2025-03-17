"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Body
from typing import Optional

from ..models.util_models import Coordinates

router = APIRouter(prefix="/mincut", tags=["Mincut"])

@router.post("/newmincut", description="This action should be used when an anomaly is detected in field that wasn't planified.\nIn this case there is no mincut created, therefore a new one will be created.")
async def new_mincut(
    coordinates: Coordinates = Body(..., title="Coordinates", description="Coordinates on which the mincut will be created"),
    workcatId: int = Body(..., title="Workcat ID", description="ID of the work associated to the anomaly", examples=[1]),
    diameter: Optional[float] = Body(..., title="Diameter (mm)", description="Diameter of the affected pipe", examples=[125]),
    depth: Optional[float] = Body(..., title="Depth (m)", description="Depth of the affected pipe", examples=[0.8]),
    material: Optional[str] = Body(..., title="Material", description="Material of the affected pipe", examples=["PE-HD"]),
    plotDistance: Optional[float] = Body(..., title="Plot Distance (m)", description="Distance for the mincut representation", examples=[1.5]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Created mincut successfully"}

@router.put("/updatemincut", description="This action should be used when a mincut is already created and it needs to be updated.")
async def update_mincut(
    coordinates: Coordinates = Body(..., title="Coordinates", description="Coordinates on which the mincut will be created"),
    workcatId: Optional[int] = Body(..., title="Workcat ID", description="ID of the work associated to the anomaly", examples=[1]),
    diameter: Optional[float] = Body(..., title="Diameter (mm)", description="Diameter of the affected pipe", examples=[125]),
    depth: Optional[float] = Body(..., title="Depth (m)", description="Depth of the affected pipe", examples=[0.8]),
    material: Optional[str] = Body(..., title="Material", description="Material of the affected pipe", examples=["PE-HD"]),
    plot_distance: Optional[float] = Body(..., title="Plot Distance (m)", description="Distance for the mincut representation", examples=[1.5]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Updated mincut successfully"}

@router.put(
        "/valveunaccess",
        description=("Recalculates the mincut when a defined one is invalid due to an inaccessible or inoperative valve. "
                     "The system excludes the problematic valve and adjusts the cut polygon based on accessible valves.")
    )
async def valve_unaccess(
    mincutId: int = Body(..., title="Mincut ID", description="ID of the mincut associated to the valve", examples=[1]),
    nodeId: int = Body(..., title="Node ID", description="ID of the node where the unaccessible valve is located", examples=[1001]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Valve unaccessed successfully"}

@router.put(
    "/startmincut",
    description="This action should be used when the mincut is ready to be executed. The system will start the mincut and the water supply will be interrupted on the affected zone."
)
async def start_mincut(
    mincutId: int = Body(..., title="Mincut ID", description="ID of the mincut to start", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Mincut started successfully"}

@router.put(
    "/endmincut",
    description=("This action should be used when the mincut has been executed and the water supply is restored. "
                 "The system will end the mincut and the affected zone will be restored.")
)
async def end_mincut(
    mincutId: int = Body(..., title="Mincut ID", description="ID of the mincut to end", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Mincut ended successfully"}

@router.put(
    "/repairmincut",
    description=("Accepts the mincut but performs the repair without interrupting the water supply. "
                 "A silent mincut is generated, allowing work on the network without affecting users.")
)
async def repair_mincut(
    mincutId: int = Body(..., title="Mincut ID", description="ID of the mincut to repair", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Mincut repaired successfully"}

@router.put(
    "/cancelmincut",
    description=("Cancels the mincut when the repair is not feasible, nullifying the planned cut while keeping the issue recorded for future resolution. "
                 "This ensures proper outage management and prevents data loss.")
)
async def cancel_mincut(
    mincutId: int = Body(..., title="Mincut ID", description="ID of the mincut to cancel", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Mincut canceled successfully"}

@router.delete(
    "/deletemincut",
    description="Deletes the mincut from the system. This action should be used when the mincut is no longer needed."
)
async def delete_mincut(
    mincutId: int = Body(..., title="Mincut ID", description="ID of the mincut to delete", examples=[1]),
    user: str = Body(..., title="User", description="User who is doing the action"),
):
    return {"message": "Mincut deleted successfully"}
