from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import JSONResponse
from models.ProjectModel import ProjectModel
from models.ChunkModule import ChnukModel
from models.db_schemes import DataChunk
from routes.schemas.nlp import NLPPushRequest, SearchRequest
from controllers import NLPController
from models.enums.ResponseEnum import ResponseSignal
import logging
from tqdm.auto import tqdm

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: int, push_request: NLPPushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)
    chunk_model =await ChnukModel.create_instance(db_client=request.app.db_client)
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client,
            request.app.template_parser
            )
    has_records = True
    page_no=1
    inserted_items_count = 0
    idx = 0

    #create collection if not existed
    collection_name = nlp_controller.create_collection_name(project_id=project.project_id)
    _ = await request.app.vector_db_client.create_collection(
        collection_name=collection_name, 
        embedding_size=request.app.embedding_client.embedding_size, 
        do_reset=push_request.do_reset)

    #setup progress bar for batchin
    total_chunks_count = await chunk_model.get_total_chunks_count_by_project(project_id=project.project_id)
    pbar = tqdm(total=total_chunks_count, desc="Indexing Chunks to VectorDB", unit="chunks", position=0)

    while has_records:

        page_chunks = await chunk_model.get_all_chunk_by_project_id(project_id=project.project_id, page=page_no)
        if len(page_chunks):
            page_no+=1

        if not page_chunks or len(page_chunks) == 0:
            has_records=False
            break
        # for qdrant
        # chunk_ids = list(range(idx, idx+len(page_chunks)))
        chunk_ids = [chunk.data_chunk_id for chunk in page_chunks]
        idx += len(page_chunks)
        
        is_inserted = await nlp_controller.index_to_vectordb(
                project=project, 
                chunks=page_chunks, 
                chunk_ids=chunk_ids)
        
        if not is_inserted:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message":ResponseSignal.INSERTD_FAILED_TO_DATABASE.value}
            )
        pbar.update(len(page_chunks))
        inserted_items_count += len(page_chunks)

    return JSONResponse(
        content={"message":ResponseSignal.INSERTED_SUCCESSFULLY_TO_DATABASE.value,
                "inserted_items_count":inserted_items_count},
    )

@nlp_router.get("/index/info/{project_id}")
async def get_index_info(request: Request, project_id: int):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client,
            request.app.template_parser

            )
    collection_information = await nlp_controller.get_vectordb_collection_info(project=project)

    return JSONResponse(
        content={"message":ResponseSignal.VECTORDB_COLLECTION_RETRIEVED_SUCCESSFULLY.value,
                "collection_information":collection_information},
    )

@nlp_router.get("/index/search/{project_id}")
async def search_project(request: Request, project_id: int, search_request:SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client,
            request.app.template_parser
            )

    results = await nlp_controller.search_vectordb_collection(project=project, text=search_request.text, limit=search_request.limit)
    if not results:
        return JSONResponse(content={"message":ResponseSignal.SEARCH_FAILED.value})
    return JSONResponse(content={"message":ResponseSignal.SEARCH_SUCCESSFULLY.value,"results":results})


@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, search_request:SearchRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create_one(project_id=project_id)

    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":ResponseSignal.PROJECT_NOT_FOUND.value}
        )

    nlp_controller = NLPController(
            request.app.vector_db_client, 
            request.app.embedding_client, 
            request.app.generation_client,
            request.app.template_parser
            )
    
    result, full_prompt, chat_history =await nlp_controller.answer_rag_question(
        project=project, 
        query=search_request.text, 
        limit=search_request.limit)

    if not result:
        return JSONResponse(content={"message":ResponseSignal.RAG_RESPONSE_GENERATED_FAILED.value})
    
    return JSONResponse(content={
        "message":ResponseSignal.RAG_RESPONSE_GENERATED_SUCCESSFULLY.value,
        "result":result, 
        "full_prompt":full_prompt, 
        "chat_history":chat_history})