from datetime import datetime

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Meeting


def make_session(tmp_path):
    engine = create_engine(f"sqlite:///{(tmp_path / 't.db').as_posix()}")
    Base.metadata.create_all(engine)
    return engine, Session(engine)


def test_ddl_has_autoincrement(tmp_path):
    engine, _ = make_session(tmp_path)
    with engine.connect() as conn:
        ddl = conn.execute(text("SELECT sql FROM sqlite_master WHERE name='meetings'")).scalar()
    assert "AUTOINCREMENT" in ddl


def test_deleted_id_is_not_reused(tmp_path):
    _, db = make_session(tmp_path)
    first = Meeting(title="a", met_at=datetime(2026, 1, 1), body="b")
    db.add(first)
    db.commit()
    first_id = first.id
    db.delete(first)
    db.commit()
    second = Meeting(title="c", met_at=datetime(2026, 1, 2), body="d")
    db.add(second)
    db.commit()
    assert second.id > first_id
