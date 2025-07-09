from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from ..util_models import BaseAPIResponse, Body, Data


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
