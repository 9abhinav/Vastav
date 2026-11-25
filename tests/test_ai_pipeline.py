import pytest
import numpy as np
from pathlib import Path
from ai.pipeline import TrafficAIPipeline

BASE_DIR = Path(__file__).resolve().parent.parent
EVIDENCE_DIR = BASE_DIR / "evidence"


def test_ai_pipeline_frame_processing():
    pipeline = TrafficAIPipeline(
        evidence_dir=EVIDENCE_DIR,
        speed_limit_kmh=60.0,
        allowed_direction="down",
        traffic_light_state="GREEN"
    )

    # Create dummy 720p frame
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    
    # Process single frame
    result = pipeline.process_frame(dummy_frame, frame_idx=1, timestamp=0.033)
    
    assert result is not None
    assert result.frame_idx == 1
    assert result.annotated_frame.shape == (720, 1280, 3)
    assert result.traffic_light_state == "GREEN"
    assert isinstance(result.to_telemetry(), dict)


def test_ai_pipeline_settings_update():
    pipeline = TrafficAIPipeline(
        evidence_dir=EVIDENCE_DIR,
        speed_limit_kmh=60.0
    )

    pipeline.update_settings({
        "speed_limit": 80.0,
        "traffic_light": {"state": "RED"},
        "allowed_direction": "up"
    })

    assert pipeline.speed_limit == 80.0
    assert pipeline.traffic_light_state == "RED"
    assert pipeline.allowed_direction == "up"
