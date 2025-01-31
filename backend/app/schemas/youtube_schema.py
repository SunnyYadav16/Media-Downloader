from typing import List, Dict
from pydantic import BaseModel, Field


class FormatRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")

class VideoRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")
    quality: str = Field(..., description="Video quality (e.g., 1080p, 720p)")
    format: str = Field(..., description="Video format (mp4, webm, mkv)")

class AudioRequest(BaseModel):
    url: str = Field(..., description="YouTube video URL")
    format: str = Field(..., description="Audio format (mp3, m4a, etc.)")
    # quality: str = Field("0", description="Audio quality (0-9, 0 is best)")

class FormatResponse(BaseModel):
    available_qualities: Dict[str, str]
    video_formats: List[str]
    audio_formats: List[str]

