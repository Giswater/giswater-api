"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from fastapi import APIRouter, Body
from typing import List, Optional
from ...utils.utils import create_body_dict, execute_procedure, create_log, handle_procedure_result
from ...models.om.profile_models import ProfileResponse
from ...dependencies import CommonsDep

router = APIRouter(prefix="/om", tags=["OM - Profile"])


@router.post(
    "/profiles",
    description="Create a new profile",
    response_model=ProfileResponse,
    response_model_exclude_unset=True,
)
async def create_profile(
    commons: CommonsDep,
    initial_node_id: int = Body(..., description="Initial node ID", examples=[35]),
    final_node_id: int = Body(..., description="Final node ID", examples=[38]),
    middle_nodes: Optional[List[int]] = Body(None, description="Middle nodes IDs", examples=[[36, 37]]),
    links_distance: int = Body(..., description="Links distance", examples=[1]),
    scale_eh: int = Body(..., description="Scale EH", examples=[1000]),
    scale_ev: int = Body(..., description="Scale EV", examples=[1000]),
):
    """Insert one or multiple hydrometers"""
    log = create_log(__name__)

    extras = {
        "initNode": initial_node_id,
        "endNode": final_node_id,
        "midNodes": middle_nodes,
        "linksDistance": links_distance,
        "scale": {"eh": scale_eh, "ev": scale_ev},
    }

    body = create_body_dict(
        device=commons["device"],
        extras=extras,
        cur_user=commons["user_id"],
    )

    result = execute_procedure(
        log,
        commons["db_manager"],
        "gw_fct_getprofilevalues",
        body,
        schema=commons["schema"],
        api_version=commons["api_version"],
    )
    return handle_procedure_result(result)
