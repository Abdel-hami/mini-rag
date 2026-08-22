from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from models.ProjectModel import ProjectModel
from models.ChunkModule import ChnukModel
from models.db_schemes import DataChunk
from routes.schemas.nlp import NLPPushRequest, SearchRequest
from controllers import NLPController
from models.enums.ResponseEnum import ResponseSignal
import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: str, push_request: NLPPushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    chunk_model =await ChnukModel.create_instance(db_client=request.app.mongodb_client)
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client
            )
    has_records = True
    page_no=1
    inserted_items_count = 0
    idx = 0

    while has_records:

        page_chunks = await chunk_model.get_all_chunk_by_project_id(project_id=project.id, page=page_no)
        if len(page_chunks):
            page_no+=1

        if not page_chunks or len(page_chunks) == 0:
            has_records=False
            break

        chunk_ids = list(range(idx, idx+len(page_chunks)))
        idx += len(page_chunks)
        
        is_inserted = nlp_controller.index_to_vectordb(
                project=project, 
                chunks=page_chunks, 
                chunk_ids=chunk_ids,
                do_reset=(push_request.do_reset
                          and inserted_items_count == 0))
        
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

@nlp_router.get("/index/info/{project_id}")
async def get_index_info(request: Request, project_id: str):

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client
            )
    collection_information = nlp_controller.get_vectordb_collection_info(project=project)

    return JSONResponse(
        content={"message":ResponseSignal.VECTORDB_COLLECTION_RETRIEVED_SUCCESSFULLY.value,
                "collection_information":collection_information},
    )

@nlp_router.get("/search/{project_id}")
async def search_project(request: Request, project_id: str, search_request:SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.mongodb_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client
            )

    results = nlp_controller.search_vectordb_collection(project=project, text=search_request.text, limit=search_request.limit)
    if not results:
        return JSONResponse(content={"message":ResponseSignal.SEARCH_FAILED.value})
    return JSONResponse(content={"message":ResponseSignal.SEARCH_SUCCESSFULLY.value,"results":results})