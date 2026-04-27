from fastapi import APIRouter

from app.api.routes_detection import router as detection_router
from app.api.routes_portal import router as portal_router
from app.api.routes_session import router as session_router

router = APIRouter()
router.include_router(session_router, tags=["sessions"])
router.include_router(detection_router, tags=["detection"])
router.include_router(portal_router, tags=["portal"])
