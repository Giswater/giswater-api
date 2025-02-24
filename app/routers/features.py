"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter, Query
from datetime import date
from typing import Literal
from ..utils import create_body_dict, execute_procedure, create_log

router = APIRouter(prefix="/features", tags=["Features"])

@router.get("/getfeaturechanges")
async def get_feature_changes(
    feature_type: Literal["FEATURE", "ELEMENT"] = Query(..., title="Feature Type", description="Type of feature to fetch"),
    action: Literal["INSERT", "UPDATE"] = Query(..., title="Action", description="Indicate wether to fetch inserts or updates"),
    lastFeeding: date = Query(..., title="Last Feeding", description="Last feeding date of the feature"),
):
    log = create_log(__name__)

    body = create_body_dict(
        feature={"feature_type": feature_type},
        extras={"action": action, "lastFeeding": lastFeeding.strftime("%Y-%m-%d")}
    )
    result = execute_procedure(log, "gw_fct_featurechanges", body)
    if not result:
        return {
            "message": "No feature changes found",
            "feature_type": feature_type,
            "action": action,
            "lastFeeding": lastFeeding
        }
    if result.get("status") != "Accepted":
        return {
            "message": "Error fetching feature changes",
            "feature_type": feature_type,
            "action": action,
            "lastFeeding": lastFeeding,
            "result": result
        }

    return {
        "message": "Fetched feature changes successfully",
        "feature_type": feature_type,
        "action": action,
        "lastFeeding": lastFeeding,
        "result": result
    }
