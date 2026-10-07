"""FastAPI 진입점. 실행: backend/ 에서 `python -m app` (포트 8000)."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api import router
from app.database import Base, engine

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="MeetingNote", lifespan=lifespan)
app.include_router(router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_request: Request, exc: RequestValidationError):
    """검증 실패는 400. 스펙 외 필드만 걸린 경우에 한해 422 로 남긴다."""
    errors = exc.errors()
    only_extra = bool(errors) and all(e["type"] == "extra_forbidden" for e in errors)
    detail = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]} for e in errors]
    return JSONResponse(status_code=422 if only_extra else 400, content={"detail": detail})
