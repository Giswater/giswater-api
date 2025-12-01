from pydantic import BaseModel, Field, field_validator
from pydantic_geojson import FeatureCollectionModel
from typing import Optional, Dict
from ..util_models import BaseAPIResponse, Body, Data, ExtentModel, Info, Message, Version, FilterFieldModel


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

# region Mincut start response models


class MincutStartData(Data):
    """Mincut start data"""
    mincutId: int = Field(..., description="Mincut id", examples=[1])
    # mincutInit: FeatureCollectionModel = Field(..., description="Mincut initial point")
    # valve: FeatureCollectionModel = Field(..., description="Valve")
    # mincutNode: FeatureCollectionModel = Field(..., description="Mincut node")
    # mincutConnec: FeatureCollectionModel = Field(..., description="Mincut connecs")
    # mincutArc: FeatureCollectionModel = Field(..., description="Mincut arcs")


class MincutStartBody(Body[MincutStartData]):
    """Body for mincut start response"""
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class MincutStartResponse(BaseAPIResponse[MincutStartBody]):
    """Response model for mincut start"""
    pass


# region Mincut cancel response models


class MincutCancelResponse(BaseAPIResponse[Dict]):
    """Response model for mincut cancel"""
    pass


# endregion


# region Mincut delete response models


class MincutDeleteResponse(BaseAPIResponse[Dict]):
    """Response model for mincut delete"""
    pass


# endregion

# endregion


# endregion


MINCUT_VALID_FIELDS = frozenset(
    ["id", "work_order", "state", "mincut_type", "exploitation", "streetaxis", "forecast_start", "forecast_end"]
)


class MincutFilterFieldsModel(BaseModel):
    """Mincut filter fields response"""
    data: Optional[Dict[str, FilterFieldModel]] = Field(None, description="Data")

    @field_validator('data')
    @classmethod
    def validate_keys(cls, v):
        for key in v.keys():
            parts = [p.strip() for p in key.split(', ')]
            if not all(p in MINCUT_VALID_FIELDS for p in parts):
                raise ValueError(f"Invalid key: '{key}'")
        return v
