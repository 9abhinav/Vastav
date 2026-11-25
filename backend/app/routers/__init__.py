from backend.app.routers.health import router as health_router
from backend.app.routers.vehicles import router as vehicles_router
from backend.app.routers.violations import router as violations_router
from backend.app.routers.statistics import router as statistics_router
from backend.app.routers.settings import router as settings_router
from backend.app.routers.cameras import router as cameras_router
from backend.app.routers.video import router as video_router
from backend.app.routers.stream import router as stream_router

__all__ = [
    "health_router",
    "vehicles_router",
    "violations_router",
    "statistics_router",
    "settings_router",
    "cameras_router",
    "video_router",
    "stream_router"
]
