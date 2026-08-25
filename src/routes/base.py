from fastapi import APIRouter, Depends
from helpers.config import get_config, Config
base_router = APIRouter(
    prefix="/api/v1",
    tags=["api_v1"],
)

@base_router.get("/")
async def root(config: Config = Depends(get_config)):
    return {
        "app_name": config.APP_NAME,
        "version": config.VERSION,
    }