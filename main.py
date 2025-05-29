from fastapi import FastAPI, File, UploadFile
import torch
import whisper
import tempfile
import os

app = FastAPI()

model_name = os.getenv("WHISPER_MODEL", "base")
device = os.getenv("WHISPER_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
print(f"Loading Whisper model: {model_name} on device: {device}")
model = whisper.load_model(model_name, device=device)
print("Whisper model loaded.")

@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await audio_file.read())
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path)
    finally:
        os.remove(tmp_path)

    return {"text": result["text"], "segments": result["segments"]}

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model is not None}