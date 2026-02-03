"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from typing import List, Optional, Dict

from pydantic import BaseModel, Field

from ..util_models import BaseAPIResponse, Body


class BaseMapzone(BaseModel):
    placeholder_field: Optional[str] = Field(None, description="Placeholder field for mapzone columns")

    class Config:
        extra = "allow"


class Macrosector(BaseMapzone):
    pass


class Sector(BaseMapzone):
    pass


class Presszone(BaseMapzone):
    pass


class Macrodma(BaseMapzone):
    pass


class Macrodqa(BaseMapzone):
    pass


class Dqa(BaseMapzone):
    pass


class Macroomzone(BaseMapzone):
    pass


class Omzone(BaseMapzone):
    pass


class Omunit(BaseMapzone):
    pass


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
