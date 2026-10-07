from datetime import datetime, timezone
from typing import Annotated

from pydantic import BaseModel, ConfigDict, StringConstraints, field_serializer, field_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Body = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


def to_utc_naive(value: datetime) -> datetime:
    """tz 가 있으면 UTC 로 바꾸고, 없으면 이미 UTC 로 본다. 저장은 tz 없는 UTC."""
    if value.tzinfo is not None:
        value = value.astimezone(timezone.utc).replace(tzinfo=None)
    return value


class NoteCreate(BaseModel):
    """POST 본문. 스펙 외 필드는 거부한다 (summary/decisions/todos 는 서버가 채운다)."""

    model_config = ConfigDict(extra="forbid")

    title: Title
    met_at: datetime
    attendees: str | None = None
    body: Body

    _utc = field_validator("met_at")(to_utc_naive)


class NoteUpdate(BaseModel):
    """PUT 본문. 보낸 필드만 덮어쓰고, 안 보낸 선택 필드는 그대로 둔다."""

    model_config = ConfigDict(extra="forbid")

    title: Title
    met_at: datetime
    attendees: str | None = None
    body: Body
    summary: str | None = None
    decisions: str | None = None
    todos: str | None = None

    _utc = field_validator("met_at")(to_utc_naive)


class _NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    met_at: datetime
    attendees: str | None
    summary: str | None
    decisions: str | None
    todos: str | None

    @field_serializer("met_at")
    def _serialize_met_at(self, value: datetime) -> str:
        # 저장값은 UTC 이므로 Z 를 붙여 돌려준다 (화면이 로컬로 되돌린다)
        return value.isoformat() + "Z"


class NoteListItem(_NoteOut):
    """목록용. body 를 뺀다."""


class NoteDetail(_NoteOut):
    body: str


class TodoItem(BaseModel):
    what: str
    who: str
    when: str
    note_id: int
    note_title: str


class UploadResult(BaseModel):
    text: str
