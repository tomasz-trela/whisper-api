from fastapi import File, Query, UploadFile, HTTPException, APIRouter
import tempfile
import os
import whisper
from src.config import WHISPER_DEVICE_NAME, WHISPER_MODEL_NAME

router = APIRouter()

print(f"Loading Whisper model: {WHISPER_MODEL_NAME} on device: {WHISPER_DEVICE_NAME}")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME, device=WHISPER_DEVICE_NAME)
print("Whisper model loaded.")


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str | None = Query(None, description="Language code, e.g. 'pl' for Polish, 'en' for English")
):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as tmp:
        tmp.write(await audio_file.read())
        tmp_path = tmp.name

    try:
        fp16_setting = True if WHISPER_DEVICE_NAME == "cuda" else False

        if language:
            result = whisper_model.transcribe(tmp_path, fp16=fp16_setting, language=language)
        else:
            result = whisper_model.transcribe(tmp_path, fp16=fp16_setting)

    except Exception as e:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return {"text": result["text"], "segments": result["segments"]}

@router.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": whisper_model is not None}