"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query
from datetime import date
from typing import Literal

router = APIRouter(prefix="/features", tags=["Features"])

@router.get("/getfeaturechanges")
async def get_feature_changes(
    feature_type: Literal["FEATURE", "ELEMENT"] = Query(..., title="Feature Type", description="Type of feature to fetch"),
    action: Literal["INSERT", "UPDATE"] = Query(..., title="Action", description="Indicate wether to fetch inserts or updates"),
    lastFeeding: date = Query(..., title="Last Feeding", description="Last feeding date of the feature"),
):
    return {
        "message": "Fetched feature changes successfully",
        "feature_type": feature_type,
        "action": action,
        "lastFeeding": lastFeeding
    }
