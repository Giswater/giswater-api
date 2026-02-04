"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from ....dependencies import CommonsDep
from ....models.om.mapzone_models import GetMacrodqasResponse, GetDqasResponse
from ....utils.utils import create_log, execute_sql_select, get_db_version

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/macrodqas",
    description="Returns a collection of macrodqas.",
    response_model=GetMacrodqasResponse,
    response_model_exclude_unset=True,
)
async def get_macrodqas(commons: CommonsDep):
    log = create_log(__name__)

    macrodqas = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="macrodqa",
        columns=None,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched macrodqas successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"macrodqas": macrodqas}},
    }


@router.get(
    "/dqas",
    description="Returns a collection of dqas.",
    response_model=GetDqasResponse,
    response_model_exclude_unset=True,
)
async def get_dqas(commons: CommonsDep):
    log = create_log(__name__)

    dqas = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="dqa",
        columns=None,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched dqas successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"dqas": dqas}},
    }
