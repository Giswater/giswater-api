from pydantic import BaseModel, Field
from typing import Any

class NodeValueUpdate(BaseModel):
    node_id: str = Field(..., title="Node ID", description="ID of the node to update", examples=["J1"])
    parameter: str = Field(..., title="Parameter", description="Parameter to update", examples=["invertElev", "maxDepth"])
    value: Any = Field(..., title="Value", description="Value", examples=[31.33, 2.26])

class LinkValueUpdate(BaseModel):
    link_id: str = Field(..., title="Link ID", description="ID of the link to update", examples=["L1"])
    parameter: str = Field(..., title="Parameter", description="Parameter to update", examples=["length", "diameter"])
    value: float = Field(..., title="Value", description="Value", examples=[10.5, 0.8])

class PumpValueUpdate(BaseModel):
    pump_id: str = Field(..., title="Pump ID", description="ID of the pump to update", examples=["P1"])
    parameter: str = Field(..., title="Parameter", description="Parameter to update", examples=["power", "speed"])
    value: float = Field(..., title="Value", description="Value", examples=[50.0, 1500])

class OverflowValueUpdate(BaseModel):
    overflow_id: str = Field(..., title="Overflow ID", description="ID of the overflow structure to update", examples=["O1"])
    parameter: str = Field(..., title="Parameter", description="Parameter to update", examples=["height", "width"])
    value: float = Field(..., title="Value", description="Value", examples=[2.0, 1.5])

class ControlValueUpdate(BaseModel):
    control_id: str = Field(..., title="Control ID", description="ID of the control structure to update", examples=["C1"])
    parameter: str = Field(..., title="Parameter", description="Parameter to update", examples=["setpoint", "threshold"])
    value: float = Field(..., title="Value", description="Value", examples=[5.0, 10.0])
