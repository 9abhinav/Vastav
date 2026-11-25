import time
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import cv2
import numpy as np

from backend.app.services.video_service import video_service
from backend.app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Stream"])


def generate_mjpeg_frames():
    """Generator function yielding multipart JPEG stream chunks."""
    # Placeholder black frame if no video is active
    placeholder = np.zeros((720, 1280, 3), dtype=np.uint8)
    cv2.putText(
        placeholder,
        "TRAFFIC MONITORING FEED OFFLINE - PRESS START",
        (220, 360),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (100, 100, 100),
        2
    )
    _, placeholder_bytes = cv2.imencode(".jpg", placeholder)
    placeholder_jpg = placeholder_bytes.tobytes()

    while True:
        frame_bytes = video_service.get_latest_jpeg()
        if frame_bytes is None:
            frame_bytes = placeholder_jpg

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n"
        )
        time.sleep(0.033)  # ~30 FPS


@router.get("/video/stream")
def get_live_mjpeg_stream():
    """Live MJPEG video stream with real-time HUD annotations."""
    return StreamingResponse(
        generate_mjpeg_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )


@router.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    """Real-time WebSocket endpoint for telemetry and instant violation alerts."""
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open and accept client messages if any
            data = await websocket.receive_text()
            # Handle client command e.g. change traffic light
            try:
                msg = json.loads(data)
                if msg.get("action") == "set_traffic_light":
                    video_service.set_traffic_light(msg.get("state", "GREEN"))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)
