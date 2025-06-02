from fastapi import File, Query, UploadFile, HTTPException, APIRouter
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from src.config import WHISPER_DEVICE_NAME, WHISPER_MODEL_NAME

router = APIRouter()

model_id = WHISPER_MODEL_NAME  
device = WHISPER_DEVICE_NAME  

print(f"Loading Hugging Face model: {model_id} on device: {device}")

torch_dtype = torch.float16 if "cuda" in device else torch.float32

try:
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
    )
    model.to(device)


    processor = AutoProcessor.from_pretrained(model_id)

    transcription_pipeline = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        max_new_tokens=128,
        chunk_length_s=30, 
        batch_size=16,     
        torch_dtype=torch_dtype,
        device=device,
    )
    print("Hugging Face pipeline loaded successfully.")

except Exception as e:
    print(f"Error loading model or pipeline: {e}")
    transcription_pipeline = None


@router.post("/transcribe")
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str | None = Query(None, description="Language code, e.g. 'pl' for Polish, 'en' for English")
):
    if transcription_pipeline is None:
        raise HTTPException(status_code=503, detail="Transcription model is not available.")

    audio_bytes = await audio_file.read()

    try:
        generate_kwargs = {}
        if language:
            generate_kwargs["language"] = language
            generate_kwargs["task"] = "transcribe"

        result = transcription_pipeline(audio_bytes, generate_kwargs=generate_kwargs, return_timestamps=True)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

    segments = result.get("chunks", [])
    
    return {"text": result["text"].strip(), "segments": segments}

@router.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": transcription_pipeline is not None}