from fastapi import Query, HTTPException, Request


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
