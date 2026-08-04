from fastapi import FastAPI
from routes.base import base_router
app = FastAPI()
# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
app.include_router(base_router)