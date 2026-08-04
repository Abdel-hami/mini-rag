from fastapi import FastAPI
app = FastAPI()
# uvicorn app:app --reload --ip 0.0.0.0 - ip forwarding to access the app from outside the container
@app.get("/hello")
def hello():
    return {"message": "Hello, World!"}