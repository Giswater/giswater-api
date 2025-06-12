from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from .util_models import BaseAPIResponse, Body, Data, ExtentModel, Message, Version, UserValue, Form, FormTab


# region Input parameters

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

# endregion
