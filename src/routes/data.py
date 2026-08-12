## it is not just another simple rag project
from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_config, Config
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from .schemas.data import ProcessRequest
import logging
logger = logging.getLogger('uvicorn.error')







data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}") ## project_id is a path parameter
async def upload_file(request: Request, project_id: str, file: UploadFile, config: Config = Depends(get_config)):

    project_model = ProjectModel(db_client=request.app.mongodb_client)

    project = await project_model.get_project_or_get_one(project_id=project_id)

    # validate file properties
    data_controller = DataController()
    is_valid, message = data_controller.validatefile(file)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": message}, ## .value to get the string value of the enum
        )

    project_dir_path = ProjectController().get_project_path(project_id = project_id)
    file_path, file_id = data_controller.generate_unique_filepath(file.filename, project_id)
    try:
        async with aiofiles.open(file_path, 'wb') as f:
            while chunk := await file.read(config.FILE_DEFAULT_CHUNK_SIZE):
                await f.write(chunk)
    except Exception as e:
        logger.error(f"An error occurred while saving the file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message":ResponseSignal.FILE_NOT_UPLOADED.value },
        )
    ## we use := instead of = to assign and check the value in one line, this is called the walrus operator, means the variable is assigned and checked in the same linem checked if the file is valid


    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": message,
                "file_id": file_id,
                "project_id": str(project.id)},
    )



@data_router.post("/process/{project_id}")
async def process_file(project_id: str, process_request: ProcessRequest, ):

    file_id = process_request.file_id
    chnk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size

    process_controller = ProcessController(project_id)

    file_content = process_controller.get_file_content(file_id)

    chunks = process_controller.process_file_content(file_content, file_id, chnk_size, overlap_size)

    if file_content is None or len(chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.PROCESSING_FAILED.value},
        )

    return chunks