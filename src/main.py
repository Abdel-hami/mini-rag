from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import base, data
from helpers.config import get_config
from pymongo import AsyncMongoClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = get_config()

    print("application starting...")
    app.mongodb_conn = AsyncMongoClient(config.MONGODB_URL) ## lazy connection,and it's load in the memory so no await needed
    app.mongodb_client = app.mongodb_conn[config.MONGODB_DATABASE]

    yield

    print("application shutting down...")
    await app.mongodb_conn.close()


app = FastAPI(lifespan=lifespan)
# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
app.include_router(base.base_router)
app.include_router(data.data_router)