from pydantic import BaseModel, Field
from typing import Optional

class MincutPlanParams(BaseModel):
    mincut_type: Optional[str] = Field(None, title="Mincut Type", description="Type of the mincut", examples=["Test"])
    anl_cause: Optional[str] = Field(None, title="Analysis Cause", description="Cause of the analysis", examples=["2"])
    received_date: Optional[str] = Field(None, title="Received Date", description="Date of the received", examples=["2025-05-13T12:00"])
    anl_descript: Optional[str] = Field(None, title="Analysis Description", description="Description of the analysis", examples=["aaaaaaaaaaaaaaa"])
    forecast_start: Optional[str] = Field(None, title="Forecast Start", description="Start of the forecast", examples=["2025-05-15T14:30"])
    forecast_end: Optional[str] = Field(None, title="Forecast End", description="End of the forecast", examples=["2025-05-16T15:40"])

class MincutExecParams(BaseModel):
    exec_start: Optional[str] = Field(None, title="Execution Start", description="Start date of the mincut", examples=["2025-05-15T14:30"])
    exec_descript: Optional[str] = Field(None, title="Execution Description", description="Description of the execution", examples=["aaaaaaaaaaaaaaa"])
    exec_user: Optional[str] = Field(None, title="Execution User", description="User who is doing the action", examples=["bgeo"])
    exec_from_plot: Optional[float] = Field(None, title="Distance", description="Distance of the mincut", examples=[1.5])
    exec_depth: Optional[float] = Field(None, title="Depth", description="Depth of the mincut", examples=[0.8])
    exec_appropiate: Optional[bool] = Field(None, title="Appropriate", description="Appropriate of the mincut", examples=[True])
    exec_end: Optional[str] = Field(None, title="Execution End", description="End date of the mincut", examples=["2025-05-16T15:40"])
