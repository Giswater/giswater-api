from pydantic import BaseModel, Field

class Coordinates(BaseModel):
    xcoord: float = Field(..., title="X", description="X coordinate in the specified EPSG system", examples=[419019.0315316747])
    ycoord: float = Field(..., title="Y", description="Y coordinate in the specified EPSG system", examples=[4576692.928314688])
    epsg: int = Field(..., title="EPSG", description="EPSG code of the coordinate system", examples=[25831])
    zoomRatio: float = Field(..., title="Zoom Ratio", description="Zoom ratio of the map", examples=[1000.0])
