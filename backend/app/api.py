import logging
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app import gemini_client
from app.config import ALLOWED_AUDIO_EXTENSIONS, MAX_UPLOAD_BYTES
from app.database import get_db
from app.models import Meeting
from app.schemas import (
    NoteCreate,
    NoteDetail,
    NoteListItem,
    NoteUpdate,
    TodoItem,
    UploadResult,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")


def get_note_or_404(db: Session, note_id: int) -> Meeting:
    note = db.get(Meeting, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="회의록을 찾을 수 없다")
    return note


@router.post("/notes", response_model=NoteDetail, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)):
    note = Meeting(**payload.model_dump())
    try:
        parts = gemini_client.classify(note.body)
        note.summary = parts["summary"]
        note.decisions = parts["decisions"]
        note.todos = parts["todos"]
    except Exception:
        # 구분이 실패해도 저장은 한다. 세 갈래는 빈 값으로 둔다
        logger.exception("세 갈래 구분 실패")
        note.summary = note.decisions = note.todos = ""
    db.add(note)
    db.commit()
    return note


@router.get("/notes", response_model=list[NoteListItem])
def list_notes(
    q: str | None = None,
    from_: date | None = Query(None, alias="from"),
    to: date | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(Meeting)
    if q:
        stmt = stmt.where(
            or_(
                Meeting.title.contains(q, autoescape=True),
                Meeting.attendees.contains(q, autoescape=True),
            )
        )
    if from_ is not None:
        stmt = stmt.where(Meeting.met_at >= datetime.combine(from_, time.min))
    if to is not None:
        # to 는 그날 23:59:59 까지 포함
        stmt = stmt.where(Meeting.met_at < datetime.combine(to + timedelta(days=1), time.min))
    stmt = stmt.order_by(Meeting.met_at.desc(), Meeting.id.desc())
    return db.scalars(stmt).all()


@router.get("/notes/{note_id}", response_model=NoteDetail)
def get_note(note_id: int, db: Session = Depends(get_db)):
    return get_note_or_404(db, note_id)


@router.put("/notes/{note_id}", response_model=NoteDetail)
def update_note(note_id: int, payload: NoteUpdate, db: Session = Depends(get_db)):
    note = get_note_or_404(db, note_id)
    for field in payload.model_fields_set:
        setattr(note, field, getattr(payload, field))
    db.commit()
    return note


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = get_note_or_404(db, note_id)
    db.delete(note)
    db.commit()
    return Response(status_code=204)


@router.get("/todos", response_model=list[TodoItem])
def list_todos(db: Session = Depends(get_db)):
    stmt = select(Meeting).order_by(Meeting.met_at.asc(), Meeting.id.asc())
    items = []
    for note in db.scalars(stmt):
        for line in (note.todos or "").splitlines():
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split("|", 2)]
            parts += [""] * (3 - len(parts))
            items.append(
                TodoItem(
                    what=parts[0],
                    who=parts[1] or "미정",
                    when=parts[2],
                    note_id=note.id,
                    note_title=note.title,
                )
            )
    return items


@router.post("/upload", response_model=UploadResult)
def upload_audio(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    ext = name[name.rfind(".") :] if "." in name else ""
    mime_type = ALLOWED_AUDIO_EXTENSIONS.get(ext)
    if mime_type is None:
        raise HTTPException(status_code=415, detail="mp3, wav 파일만 올릴 수 있다")
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="파일은 25MB 이하여야 한다")
    try:
        text = gemini_client.transcribe(data, mime_type)
    except Exception:
        logger.exception("받아쓰기 실패")
        raise HTTPException(status_code=502, detail="받아쓰기에 실패했다")
    return UploadResult(text=text)
