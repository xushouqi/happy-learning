import asyncio
import edge_tts
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import io

router = APIRouter(prefix="/api/tts", tags=["tts"])

# Edge TTS voice for natural-sounding English
VOICE = "en-US-GuyNeural"
# Speech rate: -10% slower than normal
RATE = "+0%"


@router.get("/speak")
async def speak(text: str = Query(..., min_length=1, max_length=500)):
    """Generate TTS audio for the given English text using Edge TTS."""
    try:
        communicate = edge_tts.Communicate(text, voice=VOICE, rate=RATE)
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])

        audio_data = b"".join(chunks)

        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f'inline; filename="tts.mp3"',
                "Cache-Control": "public, max-age=3600",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="TTS generation failed")
