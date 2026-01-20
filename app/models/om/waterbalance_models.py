"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

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


class GetDmasData(BaseModel):
    dmas: List[Dma] = Field(..., description="List of DMAs")


class GetDmasBody(Body[GetDmasData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetDmasResponse(BaseAPIResponse[GetDmasBody]):
    pass


class Hydrometer(BaseModel):
    hydrometerId: int = Field(..., description="Hydrometer ID")
    hydrometerCode: str = Field(..., description="Hydrometer code")
    customerName: Optional[str] = Field(None, description="Customer name")
    featureId: int = Field(..., description="ID of the feature where the hydrometer is located")
    hydrometerCustomerCode: Optional[str] = Field(None, description="Hydrometer customer code")
    address: Optional[str] = Field(None, description="Address")
    hydroNumber: Optional[str] = Field(None, description="Hydrometer number")
    stateId: int = Field(..., description="State ID")
    startDate: Optional[str] = Field(None, description="Start date")
    endDate: Optional[str] = Field(None, description="End date")
    m3Volume: Optional[float] = Field(None, description="Volume in cubic meters")
    link: Optional[str] = Field(None, description="Link to CRM page")
    dmaId: int = Field(..., description="DMA ID")
    houseNumber: Optional[str] = Field(None, description="House number")
    idNumber: Optional[str] = Field(None, description="ID number")
    identif: Optional[str] = Field(None, description="Identification")
    explId: Optional[int] = Field(None, description="Exploration ID")
    plotCode: Optional[str] = Field(None, description="Plot code")
    priorityId: Optional[int] = Field(None, description="Priority ID")
    catalogId: Optional[int] = Field(None, description="Catalog ID")
    categoryId: Optional[int] = Field(None, description="Category ID")
    crmNumber: Optional[int] = Field(None, description="CRM number")
    muniId: Optional[int] = Field(None, description="Municipality ID")
    address1: Optional[str] = Field(None, description="Address line 1")
    address2: Optional[str] = Field(None, description="Address line 2")
    address3: Optional[str] = Field(None, description="Address line 3")
    address2_1: Optional[str] = Field(None, description="Secondary address 1")
    address2_2: Optional[str] = Field(None, description="Secondary address 2")
    address2_3: Optional[str] = Field(None, description="Secondary address 3")
    hydroManDate: Optional[str] = Field(None, description="Hydrometer manufacture date")
    updateDate: Optional[str] = Field(None, description="Update date")
    shutdownDate: Optional[str] = Field(None, description="Shutdown date")
    isWaterbal: Optional[bool] = Field(None, description="Is water balance")


class GetDmaHydrometersData(BaseModel):
    hydrometers: List[Hydrometer] = Field(default_factory=list, description="List of hydrometers")


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
