from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/api/media", tags=["media"])

VIDEO_BASE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "videos")


@router.get("/video/{filename}")
async def stream_video(filename: str):
    filepath = os.path.realpath(os.path.join(VIDEO_BASE, filename))
    if not filepath.startswith(os.path.realpath(VIDEO_BASE)):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(
        filepath,
        media_type="video/mp4",
    )
