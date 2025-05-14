from pydantic import BaseModel, Field

class MincutPlanParams(BaseModel):
    mincut_type: str = Field(..., title="Mincut Type", description="Type of the mincut", examples=["Test"])
    anl_cause: str = Field(..., title="Analysis Cause", description="Cause of the analysis", examples=["2"])
    received_date: str = Field(..., title="Received Date", description="Date of the received", examples=["2025-05-13T12:00"])
    anl_descript: str = Field(..., title="Analysis Description", description="Description of the analysis", examples=["aaaaaaaaaaaaaaa"])
    forecast_start: str = Field(..., title="Forecast Start", description="Start of the forecast", examples=["2025-05-15T14:30"])
    forecast_end: str = Field(..., title="Forecast End", description="End of the forecast", examples=["2025-05-16T15:40"])

class MincutExecParams(BaseModel):
    exec_start: str = Field(..., title="Execution Start", description="Start date of the mincut", examples=["2025-05-15T14:30"])
    exec_descript: str = Field(..., title="Execution Description", description="Description of the execution", examples=["aaaaaaaaaaaaaaa"])
    exec_user: str = Field(..., title="Execution User", description="User who is doing the action", examples=["bgeo"])
    exec_from_plot: float = Field(..., title="Distance", description="Distance of the mincut", examples=[1.5])
    exec_depth: float = Field(..., title="Depth", description="Depth of the mincut", examples=[0.8])
    exec_appropiate: bool = Field(..., title="Appropriate", description="Appropriate of the mincut", examples=[True])
    exec_end: str = Field(..., title="Execution End", description="End date of the mincut", examples=["2025-05-16T15:40"])
