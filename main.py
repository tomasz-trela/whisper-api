from fastapi import FastAPI, File, UploadFile, Request, HTTPException
from fastapi.responses import JSONResponse
import torch
import whisper
import tempfile
import os

API_KEY = os.getenv("MY_API_KEY", "domyslny_bezpieczny_klucz_api")

app = FastAPI()

model_name = os.getenv("WHISPER_MODEL", "base")
device = os.getenv("WHISPER_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
print(f"Loading Whisper model: {model_name} on device: {device}")
model = whisper.load_model(model_name, device=device)
print("Whisper model loaded.")

@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    public_paths = ["/health", "/docs", "/openapi.json"]

    if request.url.path in public_paths:
        response = await call_next(request)
        return response

    if not API_KEY:
        print("OSTRZEŻENIE: Klucz API (MY_API_KEY) nie jest skonfigurowany na serwerze. Dostęp nie jest chroniony.")
        return JSONResponse(
            status_code=500,
            content={"detail": "Błąd konfiguracji serwera: Klucz API nie został ustawiony."}
        )

    provided_api_key = request.headers.get("X-API-Key")

    if not provided_api_key:
        return JSONResponse(
            status_code=403,
            content={"detail": "Brak klucza API w nagłówku 'X-API-Key'."}
        )

    if provided_api_key != API_KEY:
        return JSONResponse(
            status_code=403,
            content={"detail": "Nieprawidłowy klucz API."}
        )

    response = await call_next(request)
    return response

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await audio_file.read())
        tmp_path = tmp.name

    try:
        fp16_setting = True if device == "cuda" else False
        result = model.transcribe(tmp_path, fp16=fp16_setting)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Błąd podczas transkrypcji: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"text": result["text"], "segments": result["segments"]}

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model is not None}
