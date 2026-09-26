from aiogram import Router
from .admin import router as admin_router
from .start import router as start_router
from .visa import router as visa_router
from .study import router as study_router
from .tour import router as tour_router
from .consultation import router as consult_router
from .status import router as status_router
from .static_info import router as static_router

main_router = Router()

# Admin router first so admin commands take precedence
main_router.include_router(admin_router)
main_router.include_router(start_router)
main_router.include_router(visa_router)
main_router.include_router(study_router)
main_router.include_router(tour_router)
main_router.include_router(consult_router)
main_router.include_router(status_router)
main_router.include_router(static_router)

__all__ = ["main_router"]
