"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from pydantic import BaseModel, Field
from pydantic_geojson import FeatureCollectionModel
from typing import List, Optional, Dict
from ..util_models import BaseAPIResponse, Body


class WaterbalanceNode(BaseModel):
    node_id: int = Field(..., description="Node ID")
    node_type: str = Field(..., description="Node type")
    node_geometry: FeatureCollectionModel = Field(..., description="Node geometry")


class WaterbalanceDma(BaseModel):
    dma_id: int = Field(..., description="DMA ID")
    dma_stylesheet: str = Field(..., description="DMA stylesheet")
    dma_geometry: FeatureCollectionModel = Field(..., description="DMA geometry")


class Waterbalance(BaseModel):
    node_id: int = Field(..., description="Node ID")
    dma_id: int = Field(..., description="DMA ID")
    flow_sign: int = Field(..., description="Flow sign")
    node: WaterbalanceNode = Field(..., description="Node")
    dma: WaterbalanceDma = Field(..., description="DMA")
    line: FeatureCollectionModel = Field(..., description="Line")


class GetWaterbalanceData(BaseModel):
    waterbalance: List[Waterbalance] = Field(default_factory=list, description="List of waterbalance")


class GetWaterbalanceBody(Body[GetWaterbalanceData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetWaterbalanceResponse(BaseAPIResponse[GetWaterbalanceBody]):
    pass
