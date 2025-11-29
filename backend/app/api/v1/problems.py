from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_problems():
    return {"message": "problems stub"}
