from fastapi import APIRouter

router = APIRouter(prefix="/digitaltwin", tags=["Digital Twin"])

@router.get("/getepafile")
async def get_epa_file():
    return {"message": "Fetched EPA file successfully"}
