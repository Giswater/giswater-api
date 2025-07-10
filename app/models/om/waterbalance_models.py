from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from ..util_models import BaseAPIResponse, Body


class Dma(BaseModel):
    dmaId: int = Field(..., description="DMA ID")
    dmaName: str = Field(..., description="DMA name")
    explId: List[int] = Field(..., description="List of exploration IDs")
    macroDmaId: Optional[int] = Field(None, description="Macro DMA ID")
    description: Optional[str] = Field(None, description="DMA description")
    active: bool = Field(..., description="Whether the DMA is active")


class ListDmasData(BaseModel):
    dmas: List[Dma] = Field(..., description="List of DMAs")


class ListDmasBody(Body[ListDmasData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class ListDmasResponse(BaseAPIResponse[ListDmasBody]):
    pass


class Hydrometer(BaseModel):
    hydrometerId: int = Field(..., description="Hydrometer ID")
    hydrometerCode: str = Field(..., description="Hydrometer code")
    customerName: Optional[str] = Field(None, description="Customer name")
    connecId: str = Field(..., description="Connection ID")
    hydrometerCustomerCode: Optional[str] = Field(None, description="Hydrometer customer code")
    address: Optional[str] = Field(None, description="Address")
    hydroNumber: Optional[str] = Field(None, description="Hydrometer number")
    stateId: int = Field(..., description="State ID")
    startDate: Optional[str] = Field(None, description="Start date")
    endDate: Optional[str] = Field(None, description="End date")
    m3Volume: Optional[float] = Field(None, description="Volume in cubic meters")
    dmaId: int = Field(..., description="DMA ID")


class GetDmaHydrometersData(BaseModel):
    hydrometers: List[Hydrometer] = Field(..., description="List of hydrometers")


class GetDmaHydrometersBody(Body[GetDmaHydrometersData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetDmaHydrometersResponse(BaseAPIResponse[GetDmaHydrometersBody]):
    pass


class Parameter(BaseModel):
    parameterId: int = Field(..., description="Parameter ID")
    parameterName: str = Field(..., description="Parameter name")
    parameterValue: float = Field(..., description="Parameter value")


class GetDmaParametersData(BaseModel):
    parameters: List[Parameter] = Field(..., description="List of parameters")


class GetDmaParametersBody(Body[GetDmaParametersData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetDmaParametersResponse(BaseAPIResponse[GetDmaParametersBody]):
    pass
