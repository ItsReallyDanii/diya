from fastapi import APIRouter

from . import auth, health, problems, recipes

router = APIRouter()
router.include_router(health.router, prefix="", tags=["health"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(problems.router, prefix="/problems", tags=["problems"])
router.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
