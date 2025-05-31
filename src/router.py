from fastapi import File, UploadFile, HTTPException
import tempfile
import os
from config import WHISPER_DEVICE_NAME
from main import whisper_model, app


@app.post("/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await audio_file.read())
        tmp_path = tmp.name

    try:
        fp16_setting = True if WHISPER_DEVICE_NAME == "cuda" else False
        result = whisper_model.transcribe(tmp_path, fp16=fp16_setting)
    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"text": result["text"], "segments": result["segments"]}

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": whisper_model is not None}