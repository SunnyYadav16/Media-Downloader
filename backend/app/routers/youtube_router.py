from fastapi import APIRouter, HTTPException

from ..core.exceptions import YouTubeDownloadError
from ..schemas.youtube_schema import FormatResponse, VideoRequest, AudioRequest, FormatRequest
from ..services.youtube_service import YouTubeService
from ..utils.validator import validate_youtube_url

yt_router = APIRouter(
    prefix="/youtube",
    tags=["YouTube"]
)
youtube_service = YouTubeService()


@yt_router.post("/formats")
async def get_formats(request: FormatRequest) -> dict:
    try:
        if not validate_youtube_url(request.url):
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL. Please provide a valid YouTube URL."
            )

        formats = await youtube_service.get_formats(request.url)

        if not formats["video_formats"] and not formats["audio_formats"]:
            raise HTTPException(
                status_code=404,
                detail="No formats found for this video. The video might be private or deleted."
            )

        return formats

    except YouTubeDownloadError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )

@yt_router.post("/download/video")
async def download_video(request: VideoRequest):
    try:
        if not validate_youtube_url(request.url):
            raise HTTPException(
                status_code=400,
                detail="Invalid YouTube URL"
            )

        # First get available formats to validate the request
        formats = await youtube_service.get_formats(request.url)

        # Validate quality
        if request.quality not in formats['available_qualities']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid quality. Available qualities: {', '.join(formats['available_qualities'].keys())}"
            )

        # Validate format
        if request.format not in formats['video_formats']:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid format. Available formats: {', '.join(formats['video_formats'])}"
            )

        result = await youtube_service.download_video(
            url=request.url,
            quality=request.quality,
            output_format=request.format
        )

        return result

    except YouTubeDownloadError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@yt_router.post("/download/audio")
async def download_audio(request: AudioRequest):
    if not validate_youtube_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    return await youtube_service.download_audio(
        url=request.url,
        audio_format=request.format,
        audio_quality="0"
    )