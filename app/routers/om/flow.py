"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Body, HTTPException
from typing import Optional, Literal
from ...utils.utils import create_body_dict, execute_procedure, create_log, handle_procedure_result
from ...models.om.flow_models import FlowResponse
from ...models.util_models import CoordinatesModel
from ...dependencies import CommonsDep

router = APIRouter(prefix="/om", tags=["OM - Flow"])


@router.post(
    "/flow",
    description="Calculate flow trace (upstream) or flow exit (downstream)",
    response_model=FlowResponse,
    response_model_exclude_unset=True,
)
async def flow(
    commons: CommonsDep,
    direction: Literal["upstream", "downstream"] = Body(..., description="Flow direction"),
    node_id: Optional[int] = Body(None, description="Node ID", examples=[35]),
    coordinates: Optional[CoordinatesModel] = Body(
        None,
        description="Coordinates of the node to calculate the flow trace",
    ),
):
    """Calculate flow trace"""
    log = create_log(__name__)

    if coordinates:
        coordinates_dict = coordinates.model_dump()
    else:
        coordinates_dict = None

    feature = None
    extras = None
    if node_id:
        feature = {"id": [node_id]}
    elif coordinates_dict:
        extras = {"coordinates": coordinates_dict}
    else:
        raise HTTPException(status_code=400, detail="Either node ID or coordinates must be provided")

    body = create_body_dict(
        device=commons["device"],
        feature=feature,
        extras=extras,
        cur_user=commons["user_id"],
    )

    procedure = "gw_fct_graphanalytics_upstream"
    if direction == "downstream":
        procedure = "gw_fct_graphanalytics_downstream"

    result = execute_procedure(
        log,
        commons["db_manager"],
        procedure,
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)
