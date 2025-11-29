from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_recipes():
    return {"message": "recipes stub"}
