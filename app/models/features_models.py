from pydantic import BaseModel, Field, ConfigDict, model_validator
from pydantic_geojson import FeatureCollectionModel
from typing import Optional, Any, List, Dict, Literal, Tuple
from typing_extensions import Self
from .util_models import BaseAPIResponse, Body, Data, ExtentModel, Message, Version, UserValue, Form, FormTab
from pyproj import Transformer


# region Input parameters

class Location(BaseModel):
    """Location model for routing"""
    x: float = Field(..., title="X coordinate", description="X coordinate in the specified EPSG system", examples=[418777.3])
    y: float = Field(..., title="Y coordinate", description="Y coordinate in the specified EPSG system", examples=[4576692.9])
    street: Optional[str] = Field(None, title="Street", description="Street name", examples=["Appleton"])
    epsg: int = Field(4326, title="EPSG", description="EPSG code of the coordinate system", examples=[4326, 25831])

    @staticmethod
    def _transform_coordinates(x: float, y: float, from_epsg: int, to_epsg: int = 4326) -> Tuple[float, float]:
        """
        Transform coordinates from one EPSG system to another.
        
        Args:
            x: X coordinate in the source EPSG system
            y: Y coordinate in the source EPSG system
            from_epsg: Source EPSG code
            to_epsg: Target EPSG code (default: 4326 - WGS84)
            
        Returns:
            Tuple of (x, y) coordinates in the target EPSG system
        """
        transformer = Transformer.from_crs(from_epsg, to_epsg, always_xy=True)
        return transformer.transform(x, y)

    @model_validator(mode='after')
    def validate_coordinates(self) -> Self:
        """Validate that coordinates are appropriate for the EPSG system"""
        if self.epsg == 4326:
            # For WGS84 (EPSG:4326), x is longitude and y is latitude
            if not (-180 <= self.x <= 180):
                raise ValueError("Longitude must be between -180 and 180 degrees")
            if not (-90 <= self.y <= 90):
                raise ValueError("Latitude must be between -90 and 90 degrees")
        return self

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary format expected by Valhalla API, transforming to EPSG:4326 if needed"""
        if self.epsg == 4326:
            return {
                "lon": self.x,
                "lat": self.y
            }

        # Transform to EPSG:4326
        transformed_x, transformed_y = self._transform_coordinates(self.x, self.y, self.epsg, 4326)
        return {
            "lon": transformed_x,
            "lat": transformed_y
        }

class ShortestPathParams(BaseModel):
    """Shortest path parameters model"""
    locations: List[Location] = Field(
        default=...,
        title="Locations",
        description="List of locations to route between",
        min_length=2,
        max_length=2
    )
    costing: Literal["auto", "pedestrian", "bicycle"] = Field(
        "auto",
        title="Costing",
        description="Mode of transport for the route",
        examples=["auto"]
    )
    units: Literal["miles", "kilometers"] = Field(
        "kilometers",
        title="Units",
        description="Units for distance measurements",
        examples=["kilometers"]
    )

# endregion

# region Response models


class GetInfoFromCoordinatesData(Data):
    """Get info from coordinates data"""
    # NOTE: fields are inherited from Data
    parentFields: List[str] = Field(..., description="Parent fields")


class GetInfoFromCoordinatesBody(Body[GetInfoFromCoordinatesData]):
    pass


class GetInfoFromCoordinatesResponse(BaseAPIResponse[GetInfoFromCoordinatesBody]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = kwargs.get("status", "Failed")
        self.message: Message = Message(**kwargs.get("message", {}))
        self.version: Version = kwargs.get("version", {})
        self.body: Body = kwargs.get("body", {})


class GetSelectorsData(Data):
    """Get selectors data"""
    # NOTE: fields are inherited from Data
    userValues: Optional[List[UserValue]] = Field(None, description="User values")
    geometry: Optional[ExtentModel] = Field(None, description="Geometry")


class FormStyle(BaseModel):
    """Form style model"""
    rowsColor: Optional[bool] = Field(None, description="Whether the selectors rows are colored or not")


class SelectorFormTab(FormTab):
    """Selector form tab model"""
    tableName: str = Field(..., description="Table name")
    selectorType: str = Field(..., description="Selector type")
    manageAll: bool = Field(..., description="Manage all")
    typeaheadFilter: Optional[str] = Field(None, description="Typeahead filter")
    selectionMode: Optional[str] = Field(None, description="Selection mode")
    typeaheadForced: bool = Field(False, description="Typeahead forced")


class SelectorForm(Form):
    """Selector form model"""
    formTabs: Optional[List[SelectorFormTab]] = Field(None, description="Form tabs")
    style: Optional[FormStyle] = Field(None, description="Form style")


class GetSelectorsBody(Body[GetSelectorsData]):
    form: Optional[SelectorForm] = Field(None, description="Selector form")
    feature: Optional[Dict[str, Any]] = Field(None, description="Feature")


class GetSelectorsResponse(BaseAPIResponse[GetSelectorsBody]):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status = kwargs.get("status", "Failed")
        self.message: Message = kwargs.get("message", {})
        self.version: Version = kwargs.get("version", {})
        self.body: Body = kwargs.get("body", {})


class GetObjectHydraulicOrderData(Data):
    """Get object hydraulic order data"""
    # NOTE: fields are inherited from Data
    hydraulicOrder: int = Field(..., description="Hydraulic order")
    objectId: int = Field(..., description="Object ID")
    objectType: str = Field(..., description="Object type")
    parentId: Optional[int] = Field(None, description="Parent ID")


class GetObjectHydraulicOrderBody(Body[GetObjectHydraulicOrderData]):
    pass


class GetObjectHydraulicOrderResponse(BaseAPIResponse[GetObjectHydraulicOrderBody]):
    pass


class GetObjectShortestPathOrderData(Data):
    """Get object shortest path order data"""
    fields: None = Field(None, description="Fields")
    path: Optional[FeatureCollectionModel] = Field(None, description="Path")
    distance: Optional[float] = Field(None, description="Distance")
    duration: Optional[float] = Field(None, description="Duration")


class GetObjectShortestPathOrderBody(Body[GetObjectShortestPathOrderData]):
    form: None = Field(None, description="Form")
    feature: None = Field(None, description="Feature")


class GetObjectShortestPathOrderResponse(BaseAPIResponse[GetObjectShortestPathOrderBody]):
    pass

# endregion
