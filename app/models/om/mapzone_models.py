"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field

from ..util_models import BaseAPIResponse, Body


class BaseMapzone(BaseModel):
    code: Optional[str] = Field(None, description="Unique code for the mapzone")
    name: Optional[str] = Field(None, description="Name of the mapzone")
    descript: Optional[str] = Field(None, description="Description of the mapzone")
    expl_id: Optional[List[int]] = Field(None, description="List of exploitation IDs")
    muni_id: Optional[List[int]] = Field(None, description="List of municipality IDs")
    addparam: Optional[Dict] = Field(None, description="Additional parameters for the mapzone")
    stylesheet: Optional[Dict] = Field(None, description="Stylesheet properties")
    link: Optional[str] = Field(None, description="Link associated with the mapzone")
    active: Optional[bool] = Field(None, description="Is the mapzone active?")
    lock_level: Optional[int] = Field(None, description="Lock level of the mapzone")
    the_geom: Optional[str] = Field(None, description="Geometry")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    created_by: Optional[str] = Field(None, description="User who created the record")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    updated_by: Optional[str] = Field(None, description="User who last updated the record")


class Macrosector(BaseMapzone):
    macrosector_id: int = Field(..., description="Macrosector ID")


class Sector(BaseMapzone):
    sector_id: int = Field(..., description="Sector ID")
    graphconfig: Optional[Dict] = Field(None, description="Graph configuration")
    avg_press: Optional[float] = Field(None, description="Average pressure")
    pattern_id: Optional[int] = Field(None, description="Pattern ID")
    sector_type: Optional[str] = Field(None, description="Sector type")
    macrosector_id: Optional[int] = Field(None, description="Macrosector ID")
    parent_id: Optional[int] = Field(None, description="Parent ID")


class Presszone(BaseMapzone):
    presszone_id: int = Field(..., description="Presszone ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    presszone_type: Optional[str] = Field(None, description="Presszone type")
    avg_press: Optional[float] = Field(None, description="Average pressure")
    graphconfig: Optional[Dict] = Field(None, description="Graph configuration")
    head: Optional[float] = Field(None, description="Head")


class Macrodma(BaseMapzone):
    macrodma_id: int = Field(..., description="Macro DMA ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")


class Macrodqa(BaseMapzone):
    macrodqa_id: int = Field(..., description="Macro DQA ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")


class Dqa(BaseMapzone):
    dqa_id: int = Field(..., description="DQA ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    graphconfig: Optional[Dict] = Field(None, description="Graph configuration")
    avg_press: Optional[float] = Field(None, description="Average pressure")
    pattern_id: Optional[int] = Field(None, description="Pattern ID")
    dqa_type: Optional[str] = Field(None, description="DQA type")
    macrodqa_id: Optional[int] = Field(None, description="Macrodqa ID")


class Macroomzone(BaseMapzone):
    macroomzone_id: int = Field(..., description="Macro roomzone ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")


class Omzone(BaseMapzone):
    omzone_id: int = Field(..., description="OM zone ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    graphconfig: Optional[Dict] = Field(None, description="Graph configuration")
    omzone_type: Optional[str] = Field(None, description="OM zone type")
    macroomzone_id: Optional[int] = Field(None, description="Macroomzone ID")


class OmunitBase(BaseModel):
    expl_id: Optional[List[int]] = Field(None, description="List of exploitation IDs")
    muni_id: Optional[List[int]] = Field(None, description="List of municipality IDs")
    sector_id: Optional[List[int]] = Field(None, description="List of sector IDs")
    node_1: Optional[int] = Field(None, description="Node 1 ID")
    node_2: Optional[int] = Field(None, description="Node 2 ID")
    is_way_in: Optional[bool] = Field(None, description="Is the way in?")
    is_way_out: Optional[bool] = Field(None, description="Is the way out?")
    the_geom: Optional[str] = Field(None, description="Geometry")
    order_number: Optional[int] = Field(None, description="Order number")


class Omunit(OmunitBase):
    omunit_id: int = Field(..., description="OM unit ID")
    macroomunit_id: Optional[int] = Field(None, description="Macro OM unit ID")


class MacroOmunit(OmunitBase):
    macroomunit_id: int = Field(..., description="Macro OM unit ID")
    catchment_node: Optional[int] = Field(None, description="Catchment node ID")


class GetMacrosectorsData(BaseModel):
    macrosectors: List[Macrosector] = Field(default_factory=list, description="List of macrosectors")


class GetMacrosectorsBody(Body[GetMacrosectorsData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetMacrosectorsResponse(BaseAPIResponse[GetMacrosectorsBody]):
    pass


class GetSectorsData(BaseModel):
    sectors: List[Sector] = Field(default_factory=list, description="List of sectors")


class GetSectorsBody(Body[GetSectorsData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetSectorsResponse(BaseAPIResponse[GetSectorsBody]):
    pass


class GetPresszonesData(BaseModel):
    presszones: List[Presszone] = Field(default_factory=list, description="List of presszones")


class GetPresszonesBody(Body[GetPresszonesData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetPresszonesResponse(BaseAPIResponse[GetPresszonesBody]):
    pass


class GetMacrodmasData(BaseModel):
    macrodmas: List[Macrodma] = Field(default_factory=list, description="List of macrodmas")


class GetMacrodmasBody(Body[GetMacrodmasData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetMacrodmasResponse(BaseAPIResponse[GetMacrodmasBody]):
    pass


class GetMacrodqasData(BaseModel):
    macrodqas: List[Macrodqa] = Field(default_factory=list, description="List of macrodqas")


class GetMacrodqasBody(Body[GetMacrodqasData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetMacrodqasResponse(BaseAPIResponse[GetMacrodqasBody]):
    pass


class GetDqasData(BaseModel):
    dqas: List[Dqa] = Field(default_factory=list, description="List of dqas")


class GetDqasBody(Body[GetDqasData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetDqasResponse(BaseAPIResponse[GetDqasBody]):
    pass


class GetMacroomzonesData(BaseModel):
    macroomzones: List[Macroomzone] = Field(default_factory=list, description="List of macroomzones")


class GetMacroomzonesBody(Body[GetMacroomzonesData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetMacroomzonesResponse(BaseAPIResponse[GetMacroomzonesBody]):
    pass


class GetOmzonesData(BaseModel):
    omzones: List[Omzone] = Field(default_factory=list, description="List of omzones")


class GetOmzonesBody(Body[GetOmzonesData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetOmzonesResponse(BaseAPIResponse[GetOmzonesBody]):
    pass


class GetOmunitsData(BaseModel):
    omunits: List[Omunit] = Field(default_factory=list, description="List of omunits")


class GetOmunitsBody(Body[GetOmunitsData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetOmunitsResponse(BaseAPIResponse[GetOmunitsBody]):
    pass
