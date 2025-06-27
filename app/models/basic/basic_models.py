from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict, Literal, Union
from ..util_models import BaseAPIResponse, Body, Data, ExtentModel, UserValue, Form, FormTab


# region Input parameters

# endregion

# region Response models


class GetFeatureChangesFeature(BaseModel):
    """Get feature changes feature model"""
    featureClass: str = Field(..., description="Feature class")
    macroSector: int = Field(..., description="Macro sector")
    assetId: Optional[str] = Field(None, description="Asset ID")
    state: Literal[0, 1, 2, 3] = Field(..., description="State")


class GetFeatureChangesNode(GetFeatureChangesFeature):
    """Get feature changes node model"""
    nodeId: int = Field(..., description="Node ID")


class GetFeatureChangesConnec(GetFeatureChangesFeature):
    """Get feature changes connection model"""
    connecId: int = Field(..., description="Connec ID")


class GetFeatureChangesData(BaseModel):
    """Get feature changes data"""
    features: List[Union[GetFeatureChangesNode, GetFeatureChangesConnec]] = Field(..., description="Features")


class GetFeatureChangesBody(Body[GetFeatureChangesData]):
    form: Optional[Dict] = Field({}, description="Form")
    feature: Optional[Dict] = Field({}, description="Feature")


class GetFeatureChangesResponse(BaseAPIResponse[GetFeatureChangesBody]):
    pass


class GetInfoFromCoordinatesData(Data):
    """Get info from coordinates data"""
    # NOTE: fields are inherited from Data
    parentFields: List[str] = Field(..., description="Parent fields")


class GetInfoFromCoordinatesBody(Body[GetInfoFromCoordinatesData]):
    pass


class GetInfoFromCoordinatesResponse(BaseAPIResponse[GetInfoFromCoordinatesBody]):
    pass


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
    pass


class SearchResultValue(BaseModel):
    """Search result value model"""
    key: str = Field(..., description="Key")
    value: Any = Field(..., description="Value")
    displayName: str = Field(..., description="Display name")


class SearchResult(BaseModel):
    """Search result model"""
    section: str = Field(..., description="Section")
    alias: str = Field(..., description="Alias")
    execFunc: Optional[str] = Field(None, description="Exec function")
    tableName: str = Field(..., description="Table name")
    values: Optional[List[SearchResultValue]] = Field(None, description="Values")


class GetSearchData(BaseModel):
    """Get search data"""
    searchResults: List[SearchResult] = Field(..., description="Search results")


class GetSearchBody(Body[GetSearchData]):
    form: None = Field(None, description="Form")
    feature: None = Field(None, description="Feature")


class GetSearchResponse(BaseAPIResponse[GetSearchBody]):
    pass

# endregion
