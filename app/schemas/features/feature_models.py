"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import Dict, Literal

from ..common import BaseAPIResponse, Body, Data

FeatureType = Literal["node", "arc", "link", "connec", "gully"]

FEATURE_TABLE_MAP: Dict[FeatureType, str] = {
    "node": "ve_node",
    "arc": "ve_arc",
    "link": "ve_link",
    "connec": "ve_connec",
    "gully": "ve_gully",
}

FEATURE_ID_MAP: Dict[FeatureType, str] = {
    "node": "node_id",
    "arc": "arc_id",
    "link": "link_id",
    "connec": "connec_id",
    "gully": "gully_id",
}


def get_feature_table(feature_type: FeatureType) -> str:
    return FEATURE_TABLE_MAP[feature_type]


def get_feature_id_column(feature_type: FeatureType) -> str:
    return FEATURE_ID_MAP[feature_type]


class GetFeatureResponse(BaseAPIResponse[Body[Data]]):
    """Response model for a single feature form (gw_fct_getinfofromid)."""

    pass
