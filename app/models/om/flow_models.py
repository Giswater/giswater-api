"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from pydantic import Field
from typing import Any, Dict, Optional

from ..util_models import (
    BaseAPIResponse,
    Body,
    Data,
    Info,
    LayeredFeatureCollectionModel,
    ReturnManagerModel,
)


class FlowData(Data):
    """Flow trace data"""

    info: Optional[Info | Dict[str, Any]] = Field(None, description="Info payload")
    initPoint: int = Field(..., description="Initial node identifier")
    point: Optional[LayeredFeatureCollectionModel | Dict[str, Any]] = Field(None, description="Point features")
    line: Optional[LayeredFeatureCollectionModel | Dict[str, Any]] = Field(None, description="Line features")
    polygon: Optional[LayeredFeatureCollectionModel | Dict[str, Any]] = Field(None, description="Polygon features")


class FlowBody(Body[FlowData]):
    """Flow response body"""

    form: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Form")
    feature: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Feature")
    returnManager: Optional[ReturnManagerModel] = Field(None, description="Return manager")


class FlowResponse(BaseAPIResponse[FlowBody]):
    """Flow response"""

    pass
