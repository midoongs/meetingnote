from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_database_url


class Base(DeclarativeBase):
    pass


def make_engine(url: str):
    # FastAPI 는 요청마다 다른 스레드를 쓰므로 check_same_thread 를 끈다
    return create_engine(url, connect_args={"check_same_thread": False})


engine = make_engine(get_database_url())
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
