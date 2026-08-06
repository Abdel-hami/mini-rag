from fastapi import APIRouter, Depends, UploadFile, File
from helpers.config import get_config, Config
from controllers import DataController
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}") ## project_id is a path parameter
async def upload_file(project_id: str, file: UploadFile, config: Config = Depends(get_config)):
    # validate file properties
    is_valid, message = DataController().validatefile(file)
    if not is_valid:
        return {"error": message}
    return {"message": "File uploaded successfully"}
