import sys
import json
from pathlib import Path
from datetime import datetime

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from backend.app.database import engine, Base, SessionLocal
from backend.app.models.settings import SystemSetting
from backend.app.models.camera import Camera
from backend.app.schemas.settings import SystemSettingsSchema


def setup_database():
    """Initializes database schema and populates default settings and camera sources."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Default settings schema
        default_settings = SystemSettingsSchema()
        setting_record = db.query(SystemSetting).filter(SystemSetting.key == "global_config").first()
        if not setting_record:
            print("Seeding default system settings...")
            setting_record = SystemSetting(
                key="global_config",
                value=json.dumps(default_settings.model_dump()),
                description="Global traffic enforcement settings and calibration"
            )
            db.add(setting_record)

        # Default camera records
        existing_camera = db.query(Camera).first()
        if not existing_camera:
            print("Seeding default camera records...")
            cam1 = Camera(
                name="Northbound Highway - Cam 01",
                location="Northbound Expressway - KM 14",
                source="videos/sample_traffic.mp4",
                camera_type="FILE",
                is_active=True,
                status="ONLINE"
            )
            cam2 = Camera(
                name="City Center Junction - Cam 02",
                location="Main Crossroads & 4th Avenue",
                source="0",
                camera_type="WEBCAM",
                is_active=True,
                status="ONLINE"
            )
            db.add_all([cam1, cam2])

        db.commit()
        print("Database initialized and seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"Error initializing database: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    setup_database()
