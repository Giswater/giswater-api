"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter

from app.api.deps import CommonsDep
from app.schemas.om.mapzone_models import GetMacrosectorsResponse, GetSectorsResponse
from app.db.execution import execute_sql_select
from app.db.version import get_db_version
from app.utils.log_setup import create_log

router = APIRouter(prefix="/om", tags=["OM - Mapzones"])


@router.get(
    "/macrosectors",
    description="Returns a collection of macrosectors.",
    response_model=GetMacrosectorsResponse,
    response_model_exclude_unset=True,
)
async def get_macrosectors(commons: CommonsDep):
    log = create_log(__name__)

    macrosectors = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="macrosector",
        columns=None,
        schema=commons["schema"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched macrosectors successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"macrosectors": macrosectors}},
    }


@router.get(
    "/sectors",
    description="Returns a collection of sectors.",
    response_model=GetSectorsResponse,
    response_model_exclude_unset=True,
)
async def get_sectors(commons: CommonsDep):
    log = create_log(__name__)

    sectors = await execute_sql_select(
        log,
        commons["db_manager"],
        table_name="sector",
        columns=None,
        schema=commons["schema"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched sectors successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"sectors": sectors}},
    }
