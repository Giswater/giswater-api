from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from ..util_models import BaseAPIResponse, Body


# Input models

class HydrometerBase(BaseModel):
    """Base hydrometer model with all fields"""
    code: str = Field(..., description="Hydrometer code (from CRM)")
    hydroNumber: Optional[str] = Field(None, description="Hydrometer number")
    connecId: Optional[str] = Field(None, description="Connection ID (linked to connec_customer_code)")
    link: Optional[str] = Field(None, description="URL link to CRM software")
    stateId: Optional[int] = Field(None, description="State ID (catalog)")
    catalogId: Optional[int] = Field(None, description="Catalog ID")
    categoryId: Optional[int] = Field(None, description="Category ID (catalog)")
    priorityId: Optional[int] = Field(None, description="Priority ID (catalog)")
    exploitation: Optional[int] = Field(None, description="Exploitation ID")
    startDate: Optional[date] = Field(None, description="Start date")
    endDate: Optional[date] = Field(None, description="End date")
    updateDate: Optional[date] = Field(None, description="Update date")
    shutdownDate: Optional[date] = Field(None, description="Shutdown date")


class HydrometerCreate(HydrometerBase):
    """Model for creating hydrometers - code is required"""
    pass


class HydrometerUpdate(BaseModel):
    """Model for updating hydrometers - all fields optional except code"""
    code: str = Field(..., description="Hydrometer code (identifier)")
    hydroNumber: Optional[str] = Field(None, description="Hydrometer number")
    connecId: Optional[str] = Field(None, description="Connection ID (linked to connec_customer_code)")
    link: Optional[str] = Field(None, description="URL link to CRM software")
    stateId: Optional[int] = Field(None, description="State ID (catalog)")
    catalogId: Optional[int] = Field(None, description="Catalog ID")
    categoryId: Optional[int] = Field(None, description="Category ID (catalog)")
    priorityId: Optional[int] = Field(None, description="Priority ID (catalog)")
    exploitation: Optional[int] = Field(None, description="Exploitation ID")
    startDate: Optional[date] = Field(None, description="Start date")
    endDate: Optional[date] = Field(None, description="End date")
    updateDate: Optional[date] = Field(None, description="Update date")
    shutdownDate: Optional[date] = Field(None, description="Shutdown date")


# Response models

class HydrometerData(BaseModel):
    """Data returned from hydrometer operations"""
    hydrometers: Optional[List[Dict[str, Any]]] = Field(None, description="List of hydrometers affected")
    count: Optional[int] = Field(None, description="Number of hydrometers affected")


class HydrometerBody(Body[HydrometerData]):
    """Body for hydrometer response"""
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class HydrometerResponse(BaseAPIResponse[HydrometerBody]):
    """Response model for hydrometer operations"""
    pass

