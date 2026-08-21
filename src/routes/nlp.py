from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from models.ProjectModel import ProjectModel
from models.ChunkModule import ChnukModel
from models.db_schemes import DataChunk
from schemas.nlp import NLPPushRequest
from controllers import NLPController
from models.enums.ResponseEnum import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)


@nlp_router.post("index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: NLPPushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )
    
    has_records = True
    page_no=1
    inserted_items_count = 0

    while has_records:
        page_chunks = await ChnukModel.create_instance(
            db_client=request.app.mongodb_client).get_all_chunk_by_project_id(project_id=project.id, page=page_no)
        if len(page_chunks):
            page_no+=1
        if not page_chunks or len(page_chunks) == 0:
            has_records=False
            break

        is_inserted = NLPController(
            request.app.vectordb_client, 
            request.app.embedding_client, 
            request.app.generation_client
            ).index_to_vectordb(
                project=project, 
                chunks=page_chunks, 
                do_reset=push_request.do_reset)
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message":ResponseSignal.INSERTD_FAILED_TO_DATABASE.value}
            )

        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content={"message":ResponseSignal.INSERTED_SUCCESSFULLY_TO_DATABASE.value,
                "inserted_items_count":inserted_items_count},
    )