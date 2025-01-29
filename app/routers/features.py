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
