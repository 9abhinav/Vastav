import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database import get_db
from backend.app.models.settings import SystemSetting
from backend.app.schemas.settings import SystemSettingsSchema
from backend.app.services.video_service import video_service

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=SystemSettingsSchema)
def get_system_settings(db: Session = Depends(get_db)):
    """Retrieve active system settings and calibration coordinates."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "global_config").first()
    if not setting or not setting.value:
        default_cfg = SystemSettingsSchema()
        return default_cfg

    try:
        data = json.loads(setting.value)
        return SystemSettingsSchema(**data)
    except Exception:
        return SystemSettingsSchema()


@router.put("", response_model=SystemSettingsSchema)
def update_system_settings(new_settings: SystemSettingsSchema, db: Session = Depends(get_db)):
    """Update system settings, calibration points, and speed limits."""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "global_config").first()
    data_dict = new_settings.model_dump()
    json_str = json.dumps(data_dict)

    if not setting:
        setting = SystemSetting(
            key="global_config",
            value=json_str,
            description="Global traffic enforcement settings and calibration"
        )
        db.add(setting)
    else:
        setting.value = json_str

    db.commit()

    # Apply live to running video pipeline
    if video_service.pipeline:
        video_service.pipeline.update_settings(data_dict)

    return new_settings


@router.post("/traffic-light")
def set_traffic_light_state(state: str, db: Session = Depends(get_db)):
    """Quick toggle for the virtual traffic light (RED, YELLOW, GREEN)."""
    valid_states = ["RED", "YELLOW", "GREEN"]
    state_upper = state.upper()
    if state_upper not in valid_states:
        raise HTTPException(status_code=400, detail=f"Invalid state. Must be one of {valid_states}")

    video_service.set_traffic_light(state_upper)

    # Persist in DB settings
    setting = db.query(SystemSetting).filter(SystemSetting.key == "global_config").first()
    if setting and setting.value:
        try:
            cfg = json.loads(setting.value)
            if "traffic_light" not in cfg:
                cfg["traffic_light"] = {}
            cfg["traffic_light"]["state"] = state_upper
            setting.value = json.dumps(cfg)
            db.commit()
        except Exception:
            pass

    return {"status": "success", "traffic_light_state": state_upper}
