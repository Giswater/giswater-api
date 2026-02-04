"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from ....dependencies import CommonsDep
from ....models.om.mapzone_models import GetMacroomzonesResponse, GetOmzonesResponse
from ....utils.utils import create_log, execute_sql_select, get_db_version

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/macroomzones",
    description="Returns a collection of macroomzones.",
    response_model=GetMacroomzonesResponse,
    response_model_exclude_unset=True,
)
async def get_macroomzones(commons: CommonsDep):
    log = create_log(__name__)

    macroomzones = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="macroomzone",
        columns=None,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched macroomzones successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"macroomzones": macroomzones}},
    }


@router.get(
    "/omzones",
    description="Returns a collection of omzones.",
    response_model=GetOmzonesResponse,
    response_model_exclude_unset=True,
)
async def get_omzones(commons: CommonsDep):
    log = create_log(__name__)

    omzones = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="omzone",
        columns=None,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched omzones successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"omzones": omzones}},
    }
