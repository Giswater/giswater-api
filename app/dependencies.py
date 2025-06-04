from fastapi import Depends, Query, HTTPException
from .database import validate_schema


async def get_schema(schema: str = Query(..., description="Database schema name", example="public")):
    """Dependency to get and validate schema parameter"""
    if not validate_schema(schema):
        raise HTTPException(status_code=404, detail=f"Schema '{schema}' not found")
    return schema 