from pydantic import BaseModel, Field
from pydantic_geojson import FeatureCollectionModel
from typing import Optional
from ..util_models import BaseAPIResponse, Body, Data, ExtentModel, Info, Message, Version


# region Input parameters


class MincutPlanParams(BaseModel):
    mincut_type: Optional[str] = Field(
        None,
        title="Mincut Type",
        description="Type of the mincut",
        examples=["Test"]
    )
    anl_cause: Optional[str] = Field(
        None,
        title="Analysis Cause",
        description="Cause of the analysis",
        examples=["2"]
    )
    received_date: Optional[str] = Field(
        None,
        title="Received Date",
        description="Date of the received",
        examples=["2025-05-13T12:00"]
    )
    anl_descript: Optional[str] = Field(
        None,
        title="Analysis Description",
        description="Description of the analysis",
        examples=["aaaaaaaaaaaaaaa"]
    )
    forecast_start: Optional[str] = Field(
        None,
        title="Forecast Start",
        description="Start of the forecast",
        examples=["2025-05-15T14:30"]
    )
    forecast_end: Optional[str] = Field(
        None,
        title="Forecast End",
        description="End of the forecast",
        examples=["2025-05-16T15:40"]
    )


class MincutExecParams(BaseModel):
    exec_start: Optional[str] = Field(
        None,
        title="Execution Start",
        description="Start date of the mincut",
        examples=["2025-05-15T14:30"]
    )
    exec_descript: Optional[str] = Field(
        None,
        title="Execution Description",
        description="Description of the execution",
        examples=["aaaaaaaaaaaaaaa"]
    )
    exec_user: Optional[str] = Field(
        None,
        title="Execution User",
        description="User who is doing the action",
        examples=["bgeo"]
    )
    exec_from_plot: Optional[float] = Field(
        None,
        title="Distance",
        description="Distance of the mincut",
        examples=[1.5]
    )
    exec_depth: Optional[float] = Field(
        None,
        title="Depth",
        description="Depth of the mincut",
        examples=[0.8]
    )
    exec_appropiate: Optional[bool] = Field(
        None,
        title="Appropriate",
        description="Appropriate of the mincut",
        examples=[True]
    )
    exec_end: Optional[str] = Field(
        None,
        title="Execution End",
        description="End date of the mincut",
        examples=["2025-05-16T15:40"]
    )

# endregion

# region Response models


class ValveUnaccessData(Data):
    """Valve unaccess data"""
    # NOTE: fields are inherited from Data
    info: Optional[Info] = Field(None, description="Info of the data")
    mincutId: int = Field(..., description="Mincut id", examples=[1])
    mincutState: int = Field(..., description="Mincut state", examples=[1])
    mincutInit: FeatureCollectionModel = Field(..., description="Mincut initial point")
    mincutProposedValve: FeatureCollectionModel = Field(..., description="Mincut proposed valve")
    mincutNotProposedValve: FeatureCollectionModel = Field(..., description="Mincut not proposed valve")
    mincutNode: FeatureCollectionModel = Field(..., description="Mincut node")
    mincutConnec: FeatureCollectionModel = Field(..., description="Mincut connecs")
    mincutArc: FeatureCollectionModel = Field(..., description="Mincut arcs")
    tiled: bool = Field(..., description="Tiled", examples=[True])
    geometry: ExtentModel = Field(..., description="Extent of the mincut")


class ValveUnaccessBody(Body[ValveUnaccessData]):
    pass


class ValveUnaccessResponse(BaseAPIResponse[ValveUnaccessBody]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = kwargs.get("status", "Failed")
        self.message: Message = kwargs.get("message", {})
        self.version: Version = kwargs.get("version", {})
        self.body: ValveUnaccessBody = kwargs.get("body", {})

# endregion
