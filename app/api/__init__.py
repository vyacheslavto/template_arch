from fastapi import APIRouter

from app.api.utils import health_check
from app.api.v1 import router as v1_router

router = APIRouter()

# FIXME прописать свои роутеры здесь
router.include_router(v1_router, prefix="/api/v1")
router.include_router(health_check.router, prefix="/health", tags=["health"])
