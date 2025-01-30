"""
This file is part of Giswater
The program is free software: you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation, either version 3 of the License,
or (at your option) any later version.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/waterbalance", tags=["Water Balance"])

@router.get("/getdmahydrometers")
async def get_dma_hydrometers():
    return {"message": "Fetched DMA hydrometers successfully"}
