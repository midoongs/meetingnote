"""환경 설정. 키와 모델명은 .env 로만 읽는다."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
ROOT_DIR = BASE_DIR.parent  # 저장소 루트 (.env 위치)

load_dotenv(ROOT_DIR / ".env")

PORT = 8000
MAX_UPLOAD_BYTES = 25 * 1024 * 1024
ALLOWED_AUDIO_EXTENSIONS = {".mp3": "audio/mpeg", ".wav": "audio/wav"}


def get_gemini_api_key() -> str:
    return os.getenv("GEMINI_API_KEY", "")


def get_gemini_model() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")


def get_database_url() -> str:
    return os.getenv("DATABASE_URL", f"sqlite:///{(BASE_DIR / 'meetingnote.db').as_posix()}")
