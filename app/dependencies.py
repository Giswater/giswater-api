from typing import Annotated
from fastapi import Depends, Query, Header, Request, HTTPException
from fastapi_keycloak import OIDCUser
from .keycloak import get_current_user


async def get_schema(
    schema: str = Query(
        ...,
        description="Database schema name",
        example="public"
    ),
    request: Request = None,
):
    """
    Dependency to get and validate schema parameter.

    Args:
        schema: Schema name from query parameter
        request: Request object to access db_manager from app.state

    Returns:
        Schema name if valid

    Raises:
        HTTPException: If schema is not found
    """
    if request and hasattr(request.app.state, "db_manager"):
        db_manager = request.app.state.db_manager
        if not db_manager.validate_schema(schema):
            raise HTTPException(
                status_code=404,
                detail=f"Schema '{schema}' not found",
            )
    # If no db_manager available (shouldn't happen in normal operation), just return schema
    return schema


async def common_parameters(
    request: Request,
    current_user: OIDCUser = Depends(get_current_user()),
    schema: str = Depends(get_schema),
    device: int = Header(
        default=4,
        alias="X-Device",
        description=(
            "Device identifier. "
            "Valid values: 1 = Mobile, 2 = Tablet, 3 = Web Desktop, "
            "4 = QGIS Desktop, 5 = QGIS Web"
        ),
        ge=1,
        le=5,
    ),
):
    db_manager = request.app.state.db_manager
    if not db_manager.validate_schema(schema):
        raise HTTPException(status_code=404, detail=f"Schema '{schema}' not found")
    return {
        "request": request,
        "user_id": current_user.preferred_username,
        "schema": schema,
        "device": device,
        "db_manager": db_manager,
        "api_version": request.app.version,
    }


CommonsDep = Annotated[dict, Depends(common_parameters)]
