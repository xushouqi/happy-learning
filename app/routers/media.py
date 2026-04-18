from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter(prefix="/api/media", tags=["media"])

VIDEO_BASE = "/home/xsq/happy-learning/data/videos"


@router.get("/video/{filename}")
async def stream_video(filename: str):
    filepath = os.path.join(VIDEO_BASE, filename)
    if not os.path.isfile(filepath):
        raise HTTPException(status_code=404, detail="Video not found")
    return FileResponse(
        filepath,
        media_type="video/mp4",
        filename=filename,
    )
