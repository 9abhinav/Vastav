import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.database import init_db, SessionLocal
from backend.app.models.settings import SystemSetting
from backend.app.models.camera import Camera
from backend.app.schemas.settings import SystemSettingsSchema
from backend.app.routers import (
    health_router,
    vehicles_router,
    violations_router,
    statistics_router,
    settings_router,
    cameras_router,
    video_router,
    stream_router
)
from backend.app.services.video_service import video_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("traffic_system")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Traffic Monitoring System database...")
    init_db()

    # Seed default configuration if not present
    db = SessionLocal()
    try:
        setting_record = db.query(SystemSetting).filter(SystemSetting.key == "global_config").first()
        if not setting_record:
            logger.info("Seeding default system configuration...")
            default_cfg = SystemSettingsSchema()
            setting_record = SystemSetting(
                key="global_config",
                value=json.dumps(default_cfg.model_dump()),
                description="Global traffic enforcement settings and calibration"
            )
            db.add(setting_record)

        if db.query(Camera).count() == 0:
            logger.info("Seeding default cameras...")
            cam1 = Camera(
                name="Northbound Highway - Cam 01",
                location="Northbound Expressway - KM 14",
                source="videos/sample_traffic.mp4",
                camera_type="FILE",
                is_active=True,
                status="ONLINE"
            )
            db.add(cam1)
        db.commit()
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

    # Generate synthetic demo video if needed
    demo_video = settings.DIR_VIDEOS / "sample_traffic.mp4"
    if not demo_video.exists():
        try:
            logger.info("Generating synthetic traffic video for demo mode...")
            from scripts.generate_demo_video import generate_sample_traffic_video
            generate_sample_traffic_video(str(demo_video))
        except Exception as e:
            logger.warning(f"Could not generate demo video at startup: {e}")

    logger.info("Backend services started successfully.")
    yield

    # Shutdown
    logger.info("Shutting down backend services...")
    video_service.stop_processing()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-Time AI Traffic Violation Tracking System (YOLO, ByteTrack, Speed Homography, OCR, REST & WebSockets)",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static file mounts
app.mount("/evidence", StaticFiles(directory=str(settings.DIR_EVIDENCE)), name="evidence")
app.mount("/videos", StaticFiles(directory=str(settings.DIR_VIDEOS)), name="videos")

# Register API routers
app.include_router(health_router, prefix=settings.API_PREFIX)
app.include_router(vehicles_router, prefix=settings.API_PREFIX)
app.include_router(violations_router, prefix=settings.API_PREFIX)
app.include_router(statistics_router, prefix=settings.API_PREFIX)
app.include_router(settings_router, prefix=settings.API_PREFIX)
app.include_router(cameras_router, prefix=settings.API_PREFIX)
app.include_router(video_router, prefix=settings.API_PREFIX)
app.include_router(stream_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    return {
        "message": "Real-Time Vehicle Speed & Traffic Violation Tracking API",
        "docs": "/docs",
        "health": f"{settings.API_PREFIX}/health",
        "version": settings.VERSION
    }
