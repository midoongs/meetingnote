"""Gemini 호출 모듈: 받아쓰기(transcribe)와 세 갈래 구분(classify)."""
import io
import json
import logging

from google import genai
from google.genai import types

from app.config import get_gemini_api_key, get_gemini_model

logger = logging.getLogger(__name__)

# 인라인 전송은 요청 전체 20MB 한도가 있어 넘으면 Files API 로 올린다
INLINE_LIMIT_BYTES = 15 * 1024 * 1024

# 클라이언트는 모듈에 한 번 만들어 재사용한다 (매 호출마다 만들면 호출 도중 회수된다)
_client: genai.Client | None = None


def get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=get_gemini_api_key())
    return _client


TRANSCRIBE_PROMPT = (
    "이 녹취 음성을 들리는 그대로 한국어 텍스트로 받아써 줘. "
    "요약이나 설명을 붙이지 말고 받아쓴 본문만 출력해."
)

CLASSIFY_PROMPT = """아래 회의 내용을 요약 / 결정사항 / 할 일 세 갈래로 나눠라.

기준:
- 요약: 회의 전체를 3~5줄로. 새로운 사실을 지어내지 말 것.
- 결정사항: 「하기로 했다 / 확정 / 승인」 처럼 합의가 끝난 것만. 논의만 하고 안 정한 것은 넣지 말 것.
- 할 일: 담당자와 기한이 드러난 것만. 담당자가 없으면 미정으로 적을 것.
- 셋 중 어디에도 안 들어가는 잡담은 버릴 것.

기한(when)은 회의에서 말한 그대로 적고 날짜로 바꾸지 말 것.

회의 내용:
"""

CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "array", "items": {"type": "string"}},
        "decisions": {"type": "array", "items": {"type": "string"}},
        "todos": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "what": {"type": "string"},
                    "who": {"type": "string"},
                    "when": {"type": "string"},
                },
                "required": ["what", "who", "when"],
            },
        },
    },
    "required": ["summary", "decisions", "todos"],
}


def transcribe(data: bytes, mime_type: str) -> str:
    """녹취 파일을 본문 텍스트로 바꾼다. 실패하면 예외를 그대로 올린다."""
    client = get_client()
    model = get_gemini_model()
    uploaded = None
    try:
        if len(data) <= INLINE_LIMIT_BYTES:
            audio = types.Part.from_bytes(data=data, mime_type=mime_type)
        else:
            uploaded = client.files.upload(
                file=io.BytesIO(data), config=types.UploadFileConfig(mime_type=mime_type)
            )
            audio = uploaded
        response = client.models.generate_content(model=model, contents=[TRANSCRIBE_PROMPT, audio])
        text = (response.text or "").strip()
        if not text:
            raise ValueError("받아쓰기 결과가 비어 있다")
        return text
    finally:
        if uploaded is not None and uploaded.name:
            try:
                client.files.delete(name=uploaded.name)
            except Exception:
                logger.warning("업로드한 임시 파일 삭제 실패: %s", uploaded.name)


def _clean(value: str) -> str:
    # todos 한 줄은 `내용 | 담당자 | 기한` 이므로 값 안의 | 와 줄바꿈은 치운다
    return " ".join(str(value).replace("|", "/").split())


def classify(body: str) -> dict[str, str]:
    """본문을 세 갈래로 나눠 저장 형식(줄바꿈 구분 문자열)으로 돌려준다. 실패하면 예외를 올린다."""
    response = get_client().models.generate_content(
        model=get_gemini_model(),
        contents=CLASSIFY_PROMPT + body,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=CLASSIFY_SCHEMA,
        ),
    )
    data = json.loads(response.text)
    todo_lines = []
    for item in data["todos"]:
        what = _clean(item.get("what", ""))
        if not what:
            continue
        who = _clean(item.get("who", "")) or "미정"
        when = _clean(item.get("when", ""))
        todo_lines.append(f"{what} | {who} | {when}")
    return {
        "summary": "\n".join(_clean(s) for s in data["summary"] if _clean(s)),
        "decisions": "\n".join(_clean(s) for s in data["decisions"] if _clean(s)),
        "todos": "\n".join(todo_lines),
    }
