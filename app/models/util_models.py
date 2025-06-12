# flake8: noqa: E501
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Generic, TypeVar, Any


# Define a TypeVar for the body type
T = TypeVar('T')

# region DB models


class Version(BaseModel):
    """Version model"""
    db: str = Field(..., description="Database version", examples=["4.0.001"])
    api: str = Field(..., description="API version", examples=["1.0.0"])


class Message(BaseModel):
    """Message model"""
    level: Optional[int] = Field(None, description="Level of the message", ge=1, le=4)
    text: Optional[str] = Field(None, description="Message of the response")


class TabAction(BaseModel):
    """Tab action model"""
    actionName: str = Field(..., description="Action name")
    isEnabled: bool = Field(..., description="Is enabled")


class FormTab(BaseModel):
    """Form tab model"""
    tabName: str = Field(..., description="Tab name")
    tabLabel: str = Field(..., description="Tab label")
    tooltip: Optional[str] = Field(None, description="Tooltip")
    orderby: int = Field(..., description="Order by")
    tabActions: Optional[List[TabAction]] = Field(None, description="Tab actions")


class Form(BaseModel):
    """Form model"""
    formName: Optional[str] = Field(None, description="Form name")
    currentTab: Optional[str] = Field(None, description="Current tab")
    headerText: Optional[str] = Field(None, description="Header text")
    formTabs: Optional[List[FormTab]] = Field(None, description="Form tabs")
    isEditable: Optional[bool] = Field(None, description="Is editable")


class Geometry(BaseModel):
    """Geometry model"""
    x: float = Field(..., description="X")
    y: float = Field(..., description="Y")
    st_astext: str = Field(..., description="ST as text")  # ? camelCase?


class Feature(BaseModel):
    """Feature model"""
    featureType: Optional[str] = Field(None, description="Feature type")
    tableName: Optional[str] = Field(None, description="Table name")
    id: Optional[str] = Field(None, description="Feature id")
    idName: Optional[str] = Field(None, description="Feature id name")
    childType: Optional[str] = Field(None, description="Child type")
    tableParent: Optional[str] = Field(None, description="Table parent")
    geometry: Optional[Geometry] = Field(None, description="Geometry")
    zoomCanvasMargin: Optional[float] = Field(None, description="Zoom canvas margin")


class ValueRelation(BaseModel):
    """Value relation model"""
    layer: str = Field(..., description="Layer")
    activated: bool = Field(..., description="Activated")
    keyColumn: str = Field(..., description="Key column")
    nullValue: Optional[bool] = Field(None, description="Null value")
    valueColumn: str = Field(..., description="Value column")
    filterExpression: Optional[str] = Field(None, description="Filter expression")


class MaxMinValues(BaseModel):
    """Max min values model"""
    min: Optional[float | int] = Field(None, description="Min value")
    max: Optional[float | int] = Field(None, description="Max value")


class WidgetControls(BaseModel):
    """Widget controls model"""
    setMultiline: Optional[bool] = Field(None, description="Set multiline")
    labelPosition: Optional[Literal["top", "bottom", "left", "right"]] = Field(None, description="Label position")
    valueRelation: Optional[ValueRelation] = Field(None, description="Value relation")
    filterSign: Optional[Literal["=", ">", "<", ">=", "<=", "LIKE", "ILIKE", "BETWEEN"]] = Field(None, description="Filter sign")
    filterType: Optional[str] = Field(None, description="Filter type")  # TODO: define certain options
    saveValue: Optional[bool] = Field(None, description="Save value")
    widgetdim: Optional[int] = Field(None, description="Widget dimension")
    vdefault: Optional[Any] = Field(None, description="Default value")
    # vdefault_value: Optional[Any] = Field(None, description="Default value")  # FIXME: canviar a vdefault
    maxMinValues: Optional[MaxMinValues] = Field(None, description="Max min values")
    # columnId: Optional[int] = Field(None, description="Column id")  # TODO: passar a widgetfunctions parameters
    # getIndex: Optional[bool] = Field(None, description="Get index")  # TODO: passar a widgetfunctions parameters
    minRole: Optional[Literal["role_basic", "role_edit", "role_om", "role_epa", "role_master"]] = Field(None, description="Min role")
    text: Optional[str] = Field(None, description="Text")
    icon: Optional[str] = Field(None, description="Icon")  # FIXME: use the one in the stylesheet, waiting for web refactor
    tableUpsert: Optional[str] = Field(None, description="Table upsert")  # TODO: Edgar
    onContextMenu: Optional[str] = Field(None, description="On context menu")  # TODO: check what's this
    tabs: Optional[List[str]] = Field(None, description="Tabs")
    isEnabled: Optional[bool] = Field(None, description="Is enabled")  # TODO: check what's this
    style: Optional[str] = Field(None, description="Style")  # TODO: check if this is correct
    reloadFields: Optional[List[str]] = Field(None, description="Reload fields")


class WidgetFunction(BaseModel):
    """Widget function model"""
    functionName: Optional[str] = Field(None, description="Function name")
    parameters: Optional[dict[str, Any]] = Field(None, description="Parameters")
    module: Optional[str] = Field(None, description="Module")


class Stylesheet(BaseModel):
    """Stylesheet model"""
    icon: Optional[str] = Field(None, description="Icon")
    size: Optional[str] = Field(None, description="Icon size")
    label: Optional[str] = Field(None, description="Label style")
    widget: Optional[str] = Field(None, description="Widget style")


class GwField(BaseModel):
    """GwField model"""
    label: Optional[str] = Field(..., description="Field label")
    # name: int = Field(..., description="Field name")
    columnname: str = Field(..., description="Column name")
    # type: str = Field(..., description="Field type")  # TODO: only allow a few types
    datatype: Optional[str] = Field(..., description="Data type")  # TODO: only allow a few types
    value: Any = Field(None, description="Field value")
    widgetname: str = Field(..., description="Widget name")
    widgettype: str = Field(..., description="Widget type")  # TODO: only allow a few types
    # column_id: str = Field(..., description="Column id")  # FIXME: fora?
    tooltip: Optional[str] = Field(None, description="Tooltip")
    hidden: bool = Field(..., description="Is hidden")
    iseditable: bool = Field(..., description="Is editable")
    tabname: str = Field(..., description="Tab name")
    layoutname: Optional[str] = Field(..., description="Layout name")
    layoutorder: Optional[int] = Field(..., description="Layout order")
    isparent: Optional[bool] = Field(None, description="Is parent")  # ? Should it be optional?
    ismandatory: bool = Field(..., description="Is mandatory")
    isautoupdate: Optional[bool] = Field(None, description="Is auto update")  # ? Should it be optional?
    stylesheet: Optional[Stylesheet] = Field(None, description="Stylesheet")
    widgetcontrols: Optional[WidgetControls] = Field(None, description="Widget controls")
    widgetfunction: Optional[WidgetFunction] = Field(None, description="Widget functions")
    isfilter: Optional[bool] = Field(None, description="Is filter")  # ? Should it be optional?
    selectedId: Optional[str] = Field(None, description="Selected ID")
    comboIds: Optional[List[str]] = Field(None, description="Combo ids")
    comboNames: Optional[List[str]] = Field(None, description="Combo names")


class UserValue(BaseModel):
    """User value model"""
    parameter: str = Field(..., description="Parameter")
    value: Any = Field(..., description="Value")


class InfoValue(BaseModel):
    """Info value model"""
    id: int = Field(..., description="Value id")
    message: str = Field(..., description="Message")


class Info(BaseModel):
    """Info model"""
    values: List[InfoValue] = Field(..., description="Values of the info")


class Data(BaseModel):
    """Data model"""
    fields: Optional[List[GwField]] = Field(None, description="Fields of the data")


class Body(BaseModel, Generic[T]):
    """Body model"""
    form: Optional[Form] = Field(None, description="Form of the response")
    feature: Optional[Feature] = Field(None, description="Feature of the response")
    data: Optional[T] = Field(None, description="Data of the response")


class BaseAPIResponse(BaseModel, Generic[T]):
    """Base API response model with common fields"""
    status: Literal["Accepted", "Failed"] = Field(..., description="Status of the response", examples=["Accepted", "Failed"])
    message: Optional[Message] = Field(None, description="Response message")
    version: Version = Field(..., description="Version of the database and API")
    body: T = Field(..., description="Body of the response")


# endregion

# Example of a specific response type for an endpoint
class FormResponseBody(BaseModel):
    """Example of a specific response body for a form endpoint"""
    form: Form = Field(..., description="Form of the response")
    feature: Feature = Field(..., description="Feature of the response")
    data: Data = Field(..., description="Data of the response")


# Keep the original APIResponse for backward compatibility
class APIResponse(BaseAPIResponse[Body[Data]]):
    """Standard API response model (kept for backward compatibility)"""
    pass


class CoordinatesModel(BaseModel):
    xcoord: float = Field(..., title="X", description="X coordinate in the specified EPSG system", examples=[419019.0315316747])
    ycoord: float = Field(..., title="Y", description="Y coordinate in the specified EPSG system", examples=[4576692.928314688])
    epsg: int = Field(..., title="EPSG", description="EPSG code of the coordinate system", examples=[25831])
    zoomRatio: float = Field(..., title="Zoom Ratio", description="Zoom ratio of the map", examples=[1000.0])


class ExtentModel(BaseModel):
    """Extent model"""
    x1: float = Field(..., description="Minimum x coordinate", examples=[419058.97611645155])
    x2: float = Field(..., description="Maximum x coordinate", examples=[419097.86115133995])
    y1: float = Field(..., description="Minimum y coordinate", examples=[4576635.596078073])
    y2: float = Field(..., description="Maximum y coordinate", examples=[4576643.836554766])
