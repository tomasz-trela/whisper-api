from fastapi import FastAPI
import uvicorn
from src.middleware import VerifyAPIKeyMiddleware
from src.router import router


app = FastAPI()
app.include_router(router, prefix="/api/v1")
app.add_middleware(VerifyAPIKeyMiddleware)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)