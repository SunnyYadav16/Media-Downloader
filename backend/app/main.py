import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .core.config_settings import settings
from .routers.youtube_router import yt_router

app = FastAPI(debug=settings.APP_DEBUG)

# app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)

app.include_router(yt_router, prefix="/app/v1")

logger.add("log_api.log", rotation="100 MB")  # Automatically rotate log file


def get_info():
    """
    Info function.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(BASE_DIR, 'VERSION'), 'r') as fh:
        version = fh.read().strip()
    info = {
        "boilerplate_version": version,
        "fastapi_debug": app.debug
    }
    return info


@app.get("/")
async def root():
    """
    Root router.
    """
    logger.info("this is root")
    result = {
        "message": "Hello from the FastAPI Boilerplate!"
    }
    return result


@app.get("/health")
def health():
    """
    Health router.
    """
    logger.info("this is health")
    result = {
        "status": "ok",
        "info": get_info()
    }
    return result
