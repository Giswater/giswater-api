from fastapi import APIRouter

router = APIRouter(prefix="/mincut", tags=["Mincut"])

@router.post("/setmincut")
async def set_mincut():
    return {"message": "Set mincut successfully"}
