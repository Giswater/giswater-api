"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import List, Optional

from fastapi import APIRouter, Body

from app.api.deps import CommonsDep, get_service_context
from app.schemas.om.profile_models import ProfileResponse
from app.services.om.profile_service import ProfileService

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
    middle_nodes: Optional[List[int]] = Body(None, description="Middle nodes IDs", examples=[[37]]),
    links_distance: int = Body(..., description="Links distance", examples=[1]),
    scale_eh: int = Body(..., description="Scale EH", examples=[1000]),
    scale_ev: int = Body(..., description="Scale EV", examples=[1000]),
):
    """Create a profile from node IDs and display settings."""
    ctx = get_service_context(commons)
    return await ProfileService(ctx).create_profile(
        initial_node_id, final_node_id, middle_nodes, links_distance, scale_eh, scale_ev
    )
