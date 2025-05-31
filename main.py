from fastapi import FastAPI
import whisper
import uvicorn
from middleware import VerifyAPIKeyMiddleware
from src.router import router

from src.config import WHISPER_DEVICE_NAME, WHISPER_MODEL_NAME

app = FastAPI()
app.include_router(router, prefix="/api/v1")
app.add_middleware(VerifyAPIKeyMiddleware)

print(f"Loading Whisper model: {WHISPER_MODEL_NAME} on device: {WHISPER_DEVICE_NAME}")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE_NAME)
print("Whisper model loaded.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)