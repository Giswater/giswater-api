"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Query
from ...utils.utils import create_log, get_db_version, execute_sql
from ...models.om.waterbalance_models import GetWaterbalanceResponse
from ...dependencies import CommonsDep

router = APIRouter(prefix="/om", tags=["OM - Water Balance"])


@router.get(
    "/waterbalance",
    description=("Returns the water balance graph for all DMAs."),
    response_model=GetWaterbalanceResponse,
    response_model_exclude_unset=True,
)
async def get_waterbalance(
    commons: CommonsDep,
    dma_id: list[int] | None = Query(None, title="DMA ID", description="Filter by DMA ID(s)", examples=[1]),
):
    log = create_log(__name__)

    sql = """
        WITH sel_expl AS (
            SELECT selector_expl.expl_id
            FROM {schema}.selector_expl
            WHERE selector_expl.cur_user = CURRENT_USER
        )
        SELECT
            w.node_id,
            w.dma_id,
            w.flow_sign,
            json_build_object(
                'node_id', w.node_id,
                'node_type', cn.node_type,
                'node_geometry', jsonb_build_object(
                    'type', 'FeatureCollection',
                    'features', jsonb_build_array(
                        jsonb_build_object(
                            'type', 'Feature',
                            'geometry', ST_AsGeoJSON(st_transform(n.the_geom, 4326))::jsonb,
                            'properties', jsonb_build_object()
                        )
                    )
                )
            ) AS node,
            json_build_object(
                'dma_id', d.dma_id,
                'dma_stylesheet', d.stylesheet::json ->> 'featureColor'::text,
                'dma_geometry', jsonb_build_object(
                    'type', 'FeatureCollection',
                    'features', jsonb_build_array(
                        jsonb_build_object(
                            'type', 'Feature',
                            'geometry', ST_AsGeoJSON(st_transform(d.the_geom, 4326))::jsonb,
                            'properties', jsonb_build_object()
                        )
                    )
                )
            ) AS dma,
            jsonb_build_object(
                'type', 'FeatureCollection',
                'features', jsonb_build_array(
                    jsonb_build_object(
                        'type', 'Feature',
                        'geometry',
                        ST_AsGeoJSON(
                            st_transform(
                                st_makeline(n.the_geom, st_centroid(d.the_geom)), 4326
                            )
                        )::jsonb,
                        'properties', jsonb_build_object()
                    )
                )
            ) AS line
        FROM {schema}.ve_dma d
        JOIN {schema}.om_waterbalance_dma_graph w ON w.dma_id = d.dma_id
        JOIN {schema}.node n ON w.node_id = n.node_id
        JOIN {schema}.cat_node cn ON cn.id = n.nodecat_id
        WHERE EXISTS (
            SELECT 1
            FROM sel_expl
            WHERE sel_expl.expl_id = ANY (d.expl_id)
        )
        AND d.dma_id > 0
        AND n.the_geom IS NOT NULL
        AND d.the_geom IS NOT NULL
    """
    parameters = None
    if dma_id:
        sql += " AND w.dma_id = ANY(%s)"
        parameters = (dma_id,)
    waterbalance = await execute_sql(
        log,
        commons["db_manager"],
        sql,
        parameters=parameters,
        schema=commons["schema"],
        user=commons["user_id"],
    )

    db_version = await get_db_version(log, commons["db_manager"], schema=commons["schema"])

    return {
        "status": "Accepted",
        "message": {"level": 3, "text": "Fetched waterbalance successfully"},
        "version": {"api": commons["api_version"], "db": db_version},
        "body": {"form": {}, "feature": {}, "data": {"waterbalance": waterbalance}},
    }
