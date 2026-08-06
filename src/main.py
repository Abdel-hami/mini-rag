from fastapi import FastAPI
from routes import base, data
app = FastAPI()
# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
app.include_router(base.base_router)
app.include_router(data.data_router)