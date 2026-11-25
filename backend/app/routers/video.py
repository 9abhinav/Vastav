import os
import shutil
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.app.config import settings
from backend.app.schemas.video import VideoProcessingStatus, VideoStartRequest
from backend.app.services.video_service import video_service

router = APIRouter(prefix="/video", tags=["Video Processing"])


@router.get("/status", response_model=VideoProcessingStatus)
def get_video_status():
    """Retrieve active video stream processing metrics and state."""
    return video_service.get_status()


@router.post("/start", response_model=VideoProcessingStatus)
def start_video_processing(request: VideoStartRequest):
    """Start video processing on demo video, uploaded file, webcam, or RTSP stream."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    video_service.start_processing(
        source_type=request.source_type,
        video_path=request.video_path,
        webcam_index=request.webcam_index or 0,
        rtsp_url=request.rtsp_url,
        loop=loop
    )
    return video_service.get_status()


@router.post("/stop", response_model=VideoProcessingStatus)
def stop_video_processing():
    """Stop active video processing."""
    video_service.stop_processing()
    return video_service.get_status()


@router.post("/pause", response_model=VideoProcessingStatus)
def pause_video_processing():
    """Pause video processing."""
    video_service.pause_processing()
    return video_service.get_status()


@router.post("/resume", response_model=VideoProcessingStatus)
def resume_video_processing():
    """Resume video processing."""
    video_service.resume_processing()
    return video_service.get_status()


@router.post("/upload")
async def upload_traffic_video(file: UploadFile = File(...)):
    """Upload a custom MP4 traffic video file for AI processing."""
    if not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
        raise HTTPException(status_code=400, detail="Invalid video format. Supported: .mp4, .avi, .mov, .mkv")

    save_name = f"uploaded_{file.filename}"
    save_path = settings.DIR_VIDEOS / save_name

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "status": "success",
        "filename": save_name,
        "video_path": str(save_path)
    }
