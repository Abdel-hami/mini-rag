## it is not just another simple rag project
from fastapi import APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
import os
import aiofiles
from helpers.config import get_config, Config
from controllers import DataController, ProjectController, ProcessController
from models import ResponseSignal
from models.ProjectModel import ProjectModel
from models.ChunkModule import ChnukModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk, Asset
from routes.schemas.data import ProcessRequest
from models.enums.AssetTypeEnum import AssetTypeEnum
import logging
logger = logging.getLogger('uvicorn.error')







data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["api_v1", "data"],
)


@data_router.post("/upload/{project_id}") ## project_id is a path parameter
async def upload_file(request: Request, project_id: str, file: UploadFile, config: Config = Depends(get_config)):

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)

    project = await project_model.get_project_or_create_one(project_id=project_id)

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

    # store the asset into database

    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)
    asset = Asset(
        asset_name=file_id,
        asset_project_id=project.id,
        asset_type=AssetTypeEnum.FILE.value,
        asset_size=os.path.getsize(file_path)
    )
    asset_record = await asset_model.create_asset(asset)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": message,
                "file_id": str(asset_record.id)},
    )



@data_router.post("/process/{project_id}")
async def process_file(request: Request, project_id: str, process_request: ProcessRequest, ):

    chnk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset

    
    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id)

    asset_model = await AssetModel.create_instance(db_client=request.app.mongodb_client)

    project_file_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_project_record(project_id=project.id, asset_name=process_request.file_id)
        if asset_record is None:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": ResponseSignal.NO_FILE_ERROR.value},
            )
        project_file_ids = {
            asset_record.id: asset_record.asset_name
        }
    else:
        project_files = await asset_model.get_all_project_assets(asset_project_id=project.id, asset_type=AssetTypeEnum.FILE.value)
        project_file_ids = {
            record.id: record.asset_name
            for record in project_files
        }

    if len(project_file_ids) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": ResponseSignal.NO_FILE_ERROR.value},
        )

    chunk_model =await ChnukModel.create_instance(db_client=request.app.mongodb_client)
    
    if do_reset==1:
        _ = await chunk_model.delete_chunk_by_project_id(project.id)
    
    process_controller = ProcessController(project_id)
    inserted_chunks = 0


    for asset_id,file_id in project_file_ids.items():
        file_content = process_controller.get_file_content(file_id)

        if not file_content:
            logger.error(f"An error occurred while processing the file: {file_id}")
            continue


        chunks = process_controller.process_file_content(file_content, file_id, chnk_size, overlap_size)

        if file_content is None or len(chunks) == 0:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": ResponseSignal.PROCESSING_FAILED.value},
            )

        file_chunks_recoreds = [
            DataChunk(
                chunk_content=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chun_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(chunks)
        ]
     
        inserted_chunks += await chunk_model.insert_many_chunks(file_chunks_recoreds)
        num_files = len(project_file_ids)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": ResponseSignal.PROCESSING_SUCCESSFULLY.value,
                "inserted_chunks": inserted_chunks,
                "num_files": num_files},
    )