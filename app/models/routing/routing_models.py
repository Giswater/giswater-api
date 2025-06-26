from pydantic import BaseModel, Field, model_validator
from pydantic_geojson import FeatureCollectionModel
from typing import Optional, List, Dict, Literal, Tuple, Union, Any
from typing_extensions import Self
from ..util_models import BaseAPIResponse, Body, Data
from pyproj import Transformer


class Location(BaseModel):
    """Location model for routing"""
    x: float = Field(..., title="X coordinate", description="X coordinate in the specified EPSG system", examples=[418777.3])  # noqa: E501
    y: float = Field(..., title="Y coordinate", description="Y coordinate in the specified EPSG system", examples=[4576692.9])  # noqa: E501
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


class OptimalPathParams(BaseModel):
    """Optimal path parameters model"""
    locations: List[Location] = Field(
        default=...,
        title="Locations",
        description="List of locations to route between",
        min_length=2
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


class ObjectFeature(BaseModel):
    """Get object parameter order feature"""
    assetId: Optional[str] = Field(None, description="Asset ID")
    macroSector: int = Field(..., description="Macro sector")
    aresepId: Optional[str] = Field(None, description="Aresép ID")
    state: int = Field(..., description="State")
    featureClass: str = Field(..., description="Feature class")
    coordinates: Optional[Location] = Field(None, description="Coordinates")


class ObjectNode(ObjectFeature):
    """Get object parameter order node"""
    nodeId: int = Field(..., description="Node ID")


class ObjectArc(ObjectFeature):
    """Get object parameter order arc"""
    arcId: int = Field(..., description="Arc ID")


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


class Maneuver(BaseModel):
    """Maneuver model (Valhalla API schema)"""
    type: Optional[int] = Field(None, description="Maneuver type")
    instruction: Optional[str] = Field(None, description="Instruction")
    verbal_transition_alert_instruction: Optional[str] = Field(None, description="Verbal transition alert instruction")
    verbal_pre_transition_instruction: Optional[str] = Field(None, description="Verbal pre-transition instruction")
    verbal_post_transition_instruction: Optional[str] = Field(None, description="Verbal post-transition instruction")
    street_names: Optional[List[str]] = Field(None, description="Street names")
    begin_street_names: Optional[List[str]] = Field(None, description="Begin street names")
    time: Optional[float] = Field(None, description="Time")
    length: Optional[float] = Field(None, description="Length")
    begin_shape_index: Optional[int] = Field(None, description="Begin shape index")
    end_shape_index: Optional[int] = Field(None, description="End shape index")
    toll: Optional[bool] = Field(None, description="Toll")
    highway: Optional[bool] = Field(None, description="Highway")
    rough: Optional[bool] = Field(None, description="Rough")
    gate: Optional[bool] = Field(None, description="Gate")
    ferry: Optional[bool] = Field(None, description="Ferry")
    sign: Optional[dict] = Field(None, description="Sign")
    roundabout_exit_count: Optional[int] = Field(None, description="Roundabout exit count")
    depart_instruction: Optional[str] = Field(None, description="Depart instruction")
    verbal_depart_instruction: Optional[str] = Field(None, description="Verbal depart instruction")
    arrive_instruction: Optional[str] = Field(None, description="Arrive instruction")
    verbal_arrive_instruction: Optional[str] = Field(None, description="Verbal arrive instruction")
    transit_info: Optional[dict] = Field(None, description="Transit info")
    verbal_multi_cue: Optional[bool] = Field(None, description="Verbal multi cue")
    travel_mode: Optional[Literal["drive", "pedestrian", "bicycle", "transit"]] = Field(None, description="Travel mode")
    travel_type: Optional[
        Literal[
            # drive
            "car", "motorcycle", "motor_scooter", "truck", "bus",
            # pedestrian
            "foot", "wheelchair",
            # bicycle
            "road", "hybrid", "cross", "mountain",
            # transit
            "tram", "metro", "rail", "ferry", "cable_car", "gondola", "funicular"
        ]
    ] = Field(None, description="Travel type")
    bss_maneuver_type: Optional[
        Literal["NoneAction", "RentBikeAtBikeShare", "ReturnBikeAtBikeShare"]
    ] = Field(None, description="BSS maneuver type")
    bearing_before: Optional[float] = Field(None, description="Bearing before")
    bearing_after: Optional[float] = Field(None, description="Bearing after")
    lanes: Optional[List[dict]] = Field(None, description="Lanes")


class GetObjectOptimalPathOrderData(Data):
    """Get object optimal path order data"""
    fields: None = Field(None, description="Fields")
    path: Optional[FeatureCollectionModel] = Field(None, description="Path")
    distance: Optional[float] = Field(None, description="Distance")
    duration: Optional[float] = Field(None, description="Duration")
    maneuvers: Optional[List[Maneuver]] = Field(None, description="Maneuvers")
    features: Optional[List[Union[ObjectNode, ObjectArc]]] = Field(None, description="Features")


class GetObjectOptimalPathOrderBody(Body[GetObjectOptimalPathOrderData]):
    form: None = Field(None, description="Form")
    feature: None = Field(None, description="Feature")


class GetObjectOptimalPathOrderResponse(BaseAPIResponse[GetObjectOptimalPathOrderBody]):
    pass


class GetObjectParameterOrderData(Data):
    """Get object parameter order data"""
    fields: None = Field(None, description="Fields")
    features: List[Union[ObjectNode, ObjectArc]] = Field(..., description="Features")


class GetObjectParameterOrderBody(Body[GetObjectParameterOrderData]):
    form: dict = Field({}, description="Form")
    feature: dict = Field({}, description="Feature")


class GetObjectParameterOrderResponse(BaseAPIResponse[GetObjectParameterOrderBody]):
    pass
