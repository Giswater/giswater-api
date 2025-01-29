from fastapi import APIRouter

router = APIRouter(prefix="/waterbalance", tags=["Water Balance"])

@router.get("/getdmahydrometers")
async def get_dma_hydrometers():
    return {"message": "Fetched DMA hydrometers successfully"}
