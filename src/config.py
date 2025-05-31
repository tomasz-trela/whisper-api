import os
import torch


API_KEY = os.getenv("MY_API_KEY", "default_secure_api_key")
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
WHISPER_DEVICE_NAME = os.getenv("WHISPER_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")