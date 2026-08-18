from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import base, data
from helpers.config import get_config
from pymongo import AsyncMongoClient
from stores.llm import LLMProviderFactory

@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    print("application starting...")
    app.mongodb_conn = AsyncMongoClient(config.MONGODB_URL) ## lazy connection,and it's load in the memory so no await needed
    app.mongodb_client = app.mongodb_conn[config.MONGODB_DATABASE]

    llm_provider_factory = LLMProviderFactory(config)

    ## genration client
    app.generation_client = llm_provider_factory.create(provider = config.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = config.GENERATION_MODEL_ID)

    ## embedding client
    app.embedding_client = llm_provider_factory.create(provider = config.EMBEDDING_BACKEND)
    app.embedding_client.set_generation_model(model_id = config.EMBEDDING_MODEL_ID, embedding_size = config.EMBEDDING_MODEL_SIZE)

    yield

    print("application shutting down...")
    await app.mongodb_conn.close()


app = FastAPI(lifespan=lifespan)
# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
app.include_router(base.base_router)
app.include_router(data.data_router)