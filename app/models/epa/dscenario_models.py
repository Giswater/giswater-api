"""
Copyright © 2026 by BGEO. All rights reserved.
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List, Literal

from ..util_models import BaseAPIResponse, Body, FilterFieldModel

# region Value mappings

# endregion

# region Input parameters

# endregion

# region Response models

# endregion


DSCENARIO_VALID_FIELDS = frozenset(
    ["dscenario_id", "name", "descript", "dscenario_type", "parent_id", "expl_id", "active", "log"]
)


class DscenarioFilterFieldsModel(BaseModel):
    """Dscenario filter fields response"""

    data: Optional[Dict[str, FilterFieldModel]] = Field(None, description="Data")

    @field_validator("data")
    @classmethod
    def validate_keys(cls, v):
        for key in v.keys():
            parts = [p.strip() for p in key.split(", ")]
            if not all(p in DSCENARIO_VALID_FIELDS for p in parts):
                raise ValueError(f"Invalid key: '{key}'")
        return v


class DscenarioObjectData(BaseModel):
    """Data returned from dscenario object write operations"""

    items: Optional[List[Dict[str, Any]]] = Field(None, description="Affected rows")
    count: Optional[int] = Field(None, description="Number of affected rows")


class DscenarioObjectBody(Body[DscenarioObjectData]):
    """Body for dscenario object responses"""

    pass


class DscenarioObjectResponse(BaseAPIResponse[DscenarioObjectBody]):
    """Response model for dscenario object write operations"""

    pass


DscenarioObjectType = Literal[
    "connec",
    "controls",
    "demand",
    "frpump",
    "frshortpipe",
    "frvalve",
    "inlet",
    "junction",
    "pipe",
    "pump",
    "pump_additional",
    "reservoir",
    "rules",
    "shortpipe",
    "tank",
    "valve",
    "virtualpump",
    "virtualvalve",
]


def get_dscenario_table(object_type: DscenarioObjectType) -> str:
    """Return the table name for a given dscenario object type."""

    return f"ve_inp_dscenario_{object_type}"


# NOTE: These are the per-type object id column names used in path /{object_id}.
# Adjust if your schema uses different primary key columns.
DscenarioObjectIdColumnMap: Dict[DscenarioObjectType, str] = {
    "connec": "connec_id",
    "controls": "control_id",
    "demand": "demand_id",
    "frpump": "pump_id",
    "frshortpipe": "arc_id",
    "frvalve": "valve_id",
    "inlet": "inlet_id",
    "junction": "node_id",
    "pipe": "arc_id",
    "pump": "pump_id",
    "pump_additional": "pump_id",
    "reservoir": "node_id",
    "rules": "rule_id",
    "shortpipe": "arc_id",
    "tank": "node_id",
    "valve": "valve_id",
    "virtualpump": "pump_id",
    "virtualvalve": "valve_id",
}


def get_dscenario_object_id_column(object_type: DscenarioObjectType) -> str:
    """Return the id column name for a given dscenario object type."""

    return DscenarioObjectIdColumnMap[object_type]
