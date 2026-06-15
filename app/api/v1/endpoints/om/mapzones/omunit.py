"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from app.api.deps import CommonsDep
from app.schemas.om.mapzone_models import GetOmunitsResponse
from app.db.execution import execute_sql_select
from app.db.version import get_db_version
from app.utils.log_setup import create_log

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/omunits",
    description="Returns a collection of omunits.",
    response_model=GetOmunitsResponse,
    response_model_exclude_unset=True,
)
async def get_omunits(commons: CommonsDep):
    log = create_log(__name__)

    omunits = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="omunit",
        columns=None,
        schema=commons["schema"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched omunits successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"omunits": omunits}},
    }
