from pydantic import BaseModel, Field
from typing import Any


class HydrantReachabilityUpdate(BaseModel):
    hydrant_id: str = Field(
        ...,
        title="Hydrant ID",
        description="ID of the hydrant to update",
        examples=["J1"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[31.33, 2.26]
    )


class ReservoirValueUpdate(BaseModel):
    reservoir_id: str = Field(
        ...,
        title="Reservoir ID",
        description="ID of the reservoir to update",
        examples=["R1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["length", "diameter"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[10.5, 0.8]
    )


class LinkValueUpdate(BaseModel):
    link_id: str = Field(
        ...,
        title="Link ID",
        description="ID of the link to update",
        examples=["L1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["length", "diameter"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[10.5, 0.8]
    )


class ValveValueUpdate(BaseModel):
    valve_id: str = Field(
        ...,
        title="Valve ID",
        description="ID of the valve to update",
        examples=["V1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["power", "speed"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[50.0, 1500]
    )


class TankValueUpdate(BaseModel):
    tank_id: str = Field(
        ...,
        title="Tank ID",
        description="ID of the tank to update",
        examples=["T1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["height", "width"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[2.0, 1.5]
    )


class PumpValueUpdate(BaseModel):
    pump_id: str = Field(
        ...,
        title="Pump ID",
        description="ID of the pump to update",
        examples=["P1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["power", "speed"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[50.0, 1500]
    )


class JunctionValueUpdate(BaseModel):
    junction_id: str = Field(
        ...,
        title="Junction ID",
        description="ID of the overflow structure to update",
        examples=["O1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["height", "width"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[2.0, 1.5]
    )


class PatternValueUpdate(BaseModel):
    pattern_id: str = Field(
        ...,
        title="Pattern ID",
        description="ID of the pattern to update",
        examples=["P1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["setpoint", "threshold"]
    )
    value: float = Field(
        ...,
        title="Value",
        description="Value",
        examples=[5.0, 10.0]
    )


class ControlValueUpdate(BaseModel):
    control_id: str = Field(
        ...,
        title="Control ID",
        description="ID of the control structure to update",
        examples=["C1"]
    )
    parameter: str = Field(
        ...,
        title="Parameter",
        description="Parameter to update",
        examples=["setpoint", "threshold"]
    )
    value: Any = Field(
        ...,
        title="Value",
        description="Value",
        examples=[5.0, 10.0]
    )
