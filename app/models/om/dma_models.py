"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from ..util_models import BaseAPIResponse, Body


class Dma(BaseModel):
    dmaId: int = Field(..., description="DMA ID")
    dmaName: str = Field(..., description="DMA name")
    explId: List[int] = Field(..., description="List of exploration IDs")
    macroDmaId: Optional[int] = Field(None, description="Macro DMA ID")
    description: Optional[str] = Field(None, description="DMA description")
    active: bool = Field(..., description="Whether the DMA is active")
    geometry: Optional[str] = Field(None, description="DMA geometry")


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


class Connec(BaseModel):
    connec_id: Optional[int] = Field(None, description="Connec ID")
    code: Optional[str] = Field(None, description="Code")
    sys_code: Optional[str] = Field(None, description="System code")
    top_elev: Optional[float] = Field(None, description="Top elevation")
    depth: Optional[float] = Field(None, description="Depth")
    connec_type: Optional[str] = Field(None, description="Connec type")
    sys_type: Optional[str] = Field(None, description="System type")
    conneccat_id: Optional[str] = Field(None, description="Connec category ID")
    cat_matcat_id: Optional[str] = Field(None, description="Material category ID")
    cat_pnom: Optional[str] = Field(None, description="Nominal pressure")
    cat_dnom: Optional[str] = Field(None, description="Nominal diameter")
    cat_dint: Optional[float] = Field(None, description="Internal diameter")
    customer_code: Optional[str] = Field(None, description="Customer code")
    connec_length: Optional[float] = Field(None, description="Connec length")
    epa_type: Optional[str] = Field(None, description="EPA type")
    state: Optional[int] = Field(None, description="State")
    state_type: Optional[int] = Field(None, description="State type")
    arc_id: Optional[int] = Field(None, description="Arc ID")
    expl_id: Optional[int] = Field(None, description="Exploration ID")
    macroexpl_id: Optional[int] = Field(None, description="Macro exploration ID")
    muni_id: Optional[int] = Field(None, description="Municipality ID")
    sector_id: Optional[int] = Field(None, description="Sector ID")
    macrosector_id: Optional[int] = Field(None, description="Macro sector ID")
    sector_type: Optional[str] = Field(None, description="Sector type")
    supplyzone_id: Optional[int] = Field(None, description="Supply zone ID")
    supplyzone_type: Optional[str] = Field(None, description="Supply zone type")
    presszone_id: Optional[int] = Field(None, description="Pressure zone ID")
    presszone_type: Optional[str] = Field(None, description="Pressure zone type")
    presszone_head: Optional[float] = Field(None, description="Pressure zone head")
    dma_id: Optional[int] = Field(None, description="DMA ID")
    macrodma_id: Optional[int] = Field(None, description="Macro DMA ID")
    dma_type: Optional[str] = Field(None, description="DMA type")
    dqa_id: Optional[int] = Field(None, description="DQA ID")
    macrodqa_id: Optional[int] = Field(None, description="Macro DQA ID")
    dqa_type: Optional[str] = Field(None, description="DQA type")
    omzone_id: Optional[int] = Field(None, description="OM zone ID")
    omzone_type: Optional[str] = Field(None, description="OM zone type")
    crmzone_id: Optional[int] = Field(None, description="CRM zone ID")
    macrocrmzone_id: Optional[int] = Field(None, description="Macro CRM zone ID")
    crmzone_name: Optional[str] = Field(None, description="CRM zone name")
    minsector_id: Optional[int] = Field(None, description="Min sector ID")
    soilcat_id: Optional[str] = Field(None, description="Soil category ID")
    function_type: Optional[str] = Field(None, description="Function type")
    category_type: Optional[str] = Field(None, description="Category type")
    location_type: Optional[str] = Field(None, description="Location type")
    fluid_type: Optional[str] = Field(None, description="Fluid type")
    n_hydrometer: Optional[int] = Field(None, description="Number of hydrometers")
    n_inhabitants: Optional[int] = Field(None, description="Number of inhabitants")
    staticpressure: Optional[float] = Field(None, description="Static pressure")
    descript: Optional[str] = Field(None, description="Description")
    annotation: Optional[str] = Field(None, description="Annotation")
    observ: Optional[str] = Field(None, description="Observations")
    comment: Optional[str] = Field(None, description="Comment")
    link: Optional[str] = Field(None, description="Link")
    num_value: Optional[float] = Field(None, description="Numeric value")
    district_id: Optional[int] = Field(None, description="District ID")
    postcode: Optional[str] = Field(None, description="Postcode")
    streetaxis_id: Optional[str] = Field(None, description="Street axis ID")
    postnumber: Optional[int] = Field(None, description="Post number")
    postcomplement: Optional[str] = Field(None, description="Post complement")
    streetaxis2_id: Optional[str] = Field(None, description="Street axis 2 ID")
    postnumber2: Optional[int] = Field(None, description="Post number 2")
    postcomplement2: Optional[str] = Field(None, description="Post complement 2")
    region_id: Optional[int] = Field(None, description="Region ID")
    province_id: Optional[int] = Field(None, description="Province ID")
    block_code: Optional[str] = Field(None, description="Block code")
    plot_code: Optional[str] = Field(None, description="Plot code")
    workcat_id: Optional[str] = Field(None, description="Work category ID")
    workcat_id_end: Optional[str] = Field(None, description="Work category end ID")
    workcat_id_plan: Optional[str] = Field(None, description="Work category plan ID")
    builtdate: Optional[date] = Field(None, description="Built date")
    enddate: Optional[date] = Field(None, description="End date")
    ownercat_id: Optional[str] = Field(None, description="Owner category ID")
    pjoint_id: Optional[int] = Field(None, description="Pipe joint ID")
    pjoint_type: Optional[str] = Field(None, description="Pipe joint type")
    om_state: Optional[str] = Field(None, description="Operation & Maintenance state")
    conserv_state: Optional[str] = Field(None, description="Conservation state")
    accessibility: Optional[int] = Field(None, description="Accessibility")
    access_type: Optional[str] = Field(None, description="Access type")
    placement_type: Optional[str] = Field(None, description="Placement type")
    priority: Optional[str] = Field(None, description="Priority")
    brand_id: Optional[str] = Field(None, description="Brand ID")
    model_id: Optional[str] = Field(None, description="Model ID")
    serial_number: Optional[str] = Field(None, description="Serial number")
    asset_id: Optional[str] = Field(None, description="Asset ID")
    adate: Optional[str] = Field(None, description="Adate")
    adescript: Optional[str] = Field(None, description="Adescription")
    verified: Optional[int] = Field(None, description="Verified")
    datasource: Optional[int] = Field(None, description="Data source")
    label: Optional[str] = Field(None, description="Label")
    label_x: Optional[str] = Field(None, description="Label X coordinate")
    label_y: Optional[str] = Field(None, description="Label Y coordinate")
    label_rotation: Optional[float] = Field(None, description="Label rotation")
    rotation: Optional[float] = Field(None, description="Rotation")
    label_quadrant: Optional[str] = Field(None, description="Label quadrant")
    svg: Optional[str] = Field(None, description="SVG")
    inventory: Optional[bool] = Field(None, description="Inventory")
    publish: Optional[bool] = Field(None, description="Publish")
    is_operative: Optional[bool] = Field(None, description="Is operative")
    inp_type: Optional[str] = Field(None, description="INP type")
    demand_base: Optional[float] = Field(None, description="Demand base")
    demand_max: Optional[float] = Field(None, description="Demand max")
    demand_min: Optional[float] = Field(None, description="Demand min")
    demand_avg: Optional[float] = Field(None, description="Demand average")
    press_max: Optional[float] = Field(None, description="Maximum pressure")
    press_min: Optional[float] = Field(None, description="Minimum pressure")
    press_avg: Optional[float] = Field(None, description="Average pressure")
    quality_max: Optional[float] = Field(None, description="Maximum quality")
    quality_min: Optional[float] = Field(None, description="Minimum quality")
    quality_avg: Optional[float] = Field(None, description="Average quality")
    flow_max: Optional[float] = Field(None, description="Maximum flow")
    flow_min: Optional[float] = Field(None, description="Minimum flow")
    flow_avg: Optional[float] = Field(None, description="Average flow")
    vel_max: Optional[float] = Field(None, description="Maximum velocity")
    vel_min: Optional[float] = Field(None, description="Minimum velocity")
    vel_avg: Optional[float] = Field(None, description="Average velocity")
    result_id: Optional[str] = Field(None, description="Result ID")
    sector_style: Optional[str] = Field(None, description="Sector style")
    dma_style: Optional[str] = Field(None, description="DMA style")
    presszone_style: Optional[str] = Field(None, description="Pressure zone style")
    dqa_style: Optional[str] = Field(None, description="DQA style")
    supplyzone_style: Optional[str] = Field(None, description="Supply zone style")
    lock_level: Optional[int] = Field(None, description="Lock level")
    expl_visibility: Optional[List[int]] = Field(None, description="Exploration visibility")
    xcoord: Optional[float] = Field(None, description="X coordinate")
    ycoord: Optional[float] = Field(None, description="Y coordinate")
    lat: Optional[float] = Field(None, description="Latitude")
    long: Optional[float] = Field(None, description="Longitude")
    created_at: Optional[datetime] = Field(None, description="Creation date")
    created_by: Optional[str] = Field(None, description="Created by")
    updated_at: Optional[datetime] = Field(None, description="Updated date")
    updated_by: Optional[str] = Field(None, description="Updated by")
    the_geom: Optional[str] = Field(None, description="Geometry")
    p_state: Optional[int] = Field(None, description="P state")
    uuid: Optional[str] = Field(None, description="UUID")
    uncertain: Optional[bool] = Field(None, description="Uncertain")
    xyz_date: Optional[date] = Field(None, description="XYZ date")


class GetDmaConnecsData(BaseModel):
    connecs: List[Connec] = Field(default_factory=list, description="List of connecs")


class GetDmaConnecsBody(Body[GetDmaConnecsData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetDmaConnecsResponse(BaseAPIResponse[GetDmaConnecsBody]):
    pass


class GetDmaFlowmetersData(BaseModel):
    flowmeters: List[Dict[str, Any]] = Field(default_factory=list, description="List of flowmeters")


class GetDmaFlowmetersBody(Body[GetDmaFlowmetersData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetDmaFlowmetersResponse(BaseAPIResponse[GetDmaFlowmetersBody]):
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
