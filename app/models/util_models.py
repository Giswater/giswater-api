from pydantic import BaseModel, Field

class Coordinates(BaseModel):
    x: float = Field(..., title="X", description="X coordinate in the specified EPSG system", examples=[419019.0315316747])
    y: float = Field(..., title="Y", description="Y coordinate in the specified EPSG system", examples=[4576692.928314688])
    epsg: int = Field(..., title="EPSG", description="EPSG code of the coordinate system", examples=[25831])
