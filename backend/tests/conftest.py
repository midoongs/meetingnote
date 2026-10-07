import time
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db, make_engine
from app.main import app
from app.models import Meeting

MEETING_BODY = (
    "오늘 회의에서는 신규 앱 출시 일정을 논의했습니다. "
    "출시일은 다음 달 15일로 확정했습니다. "
    "김민수 과장이 다음 주 금요일까지 디자인 시안을 제출하기로 했습니다. "
    "점심 메뉴 이야기도 잠깐 나왔습니다."
)


@pytest.fixture
def session_factory(tmp_path):
    engine = make_engine(f"sqlite:///{(tmp_path / 'test.db').as_posix()}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def seed(session_factory):
    """Gemini 를 거치지 않고 DB 에 바로 회의록을 넣는다."""

    def _seed(**fields) -> int:
        data = dict(title="기획 회의", met_at=datetime(2026, 1, 10, 1, 0), body="본문", attendees="")
        data.update(fields)
        with session_factory() as db:
            note = Meeting(**data)
            db.add(note)
            db.commit()
            return note.id

    return _seed


@pytest.fixture
def gemini_gap():
    """Gemini 를 부르는 테스트가 끝나면 1초 쉬어 한도에 걸리지 않게 한다."""
    yield
    time.sleep(1)


@pytest.fixture
def broken_gemini(monkeypatch):
    """잘못된 키로 만든 클라이언트를 끼워 실제 호출이 실패하게 한다."""
    from google import genai

    from app import gemini_client

    monkeypatch.setattr(gemini_client, "_client", genai.Client(api_key="invalid-key"))
