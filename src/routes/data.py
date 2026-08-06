from fastapi import APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_config, Config
from controllers import DataController, ProjectController
data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}") ## project_id is a path parameter
async def upload_file(project_id: str, file: UploadFile, config: Config = Depends(get_config)):
    # validate file properties
    is_valid, message = DataController().validatefile(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": message}, ## .value to get the string value of the enum
        )

    project_dir_path = ProjectController().get_project_path(project_id = project_id)
    file_path = os.path.join(project_dir_path, file.filename)

    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(config.FILE_DEFAULT_CHUNK_SIZE):
            await f.write(chunk)
    ## we use := instead of = to assign and check the value in one line, this is called the walrus operator, means the variable is assigned and checked in the same linem checked if the file is valid


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": message},
    )
