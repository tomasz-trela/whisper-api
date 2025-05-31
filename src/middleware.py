from fastapi import Request
from fastapi.responses import JSONResponse
from config import API_KEY
from main import app


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    public_paths = ["/health", "/docs", "/openapi.json"]

    if request.url.path in public_paths:
        response = await call_next(request)
        return response

    if not API_KEY:
        print("WARNING: API key (MY_API_KEY) is not set on the server. Access is not protected.")
        return JSONResponse(
            status_code=500,
            content={"detail": "Server configuration error: API key is not set."}
        )

    provided_api_key = request.headers.get("X-API-Key")

    if not provided_api_key:
        return JSONResponse(
            status_code=403,
            content={"detail": "Missing API key in 'X-API-Key' header."}
        )

    if provided_api_key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={"detail": "Invalid API key."}
        )

    response = await call_next(request)
    return response