from fastapi import APIRouter

from app.api.v1.controllers import role_controller
from app.api.v1.controllers import user_controller

router = APIRouter()
router.include_router(role_controller.router, prefix="/roles", tags=["roles"])
router.include_router(user_controller.router, prefix="/users", tags=["users"])
