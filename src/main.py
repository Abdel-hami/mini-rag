from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import base, data, nlp
from helpers.config import get_config
from pymongo import AsyncMongoClient
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectoredb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    print("application starting...")
    # app.mongodb_conn = AsyncMongoClient(config.MONGODB_URL) ## lazy connection,and it's load in the memory so no await needed
    # app.mongodb_client = app.mongodb_conn[config.MONGODB_DATABASE]
    postgres_conn = f"postgresql+asyncpg://{config.POSTGRES_USERNAME}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_MAIN_DATABASE}"
    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(app.db_engine, class_=AsyncSession, expire_on_commit=False)
    llm_provider_factory = LLMProviderFactory(setting=config)

    ## genration client
    app.generation_client = llm_provider_factory.create(provider = config.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = config.GENERATION_MODEL_ID)

    ## embedding client
    app.embedding_client = llm_provider_factory.create(provider = config.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id = config.EMBEDDING_MODEL_ID, embedding_size = config.EMBEDDING_MODEL_SIZE)

    ## vector db client
    vector_db_provider_factory = VectorDBProviderFactory(config)
    app.vector_db_client = vector_db_provider_factory.create(provider=config.VECTOR_DB_BACKEND)
    await app.vector_db_client.connect()

    #template
    app.template_parser = TemplateParser(language=config.PRIMARY_LANG, default_language=config.DEFAULT_LANG)
    

    yield

    print("application shutting down...")
    # await app.mongodb_conn.close()
    await app.db_engine.dispose()
    app.vector_db_client.disconnect()


app = FastAPI(lifespan=lifespan)
# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(nlp.nlp_router)