import os
from sqlalchemy import JSON, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./oncofusion.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class CaseRecord(Base):
    __tablename__ = "cases"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    payload: Mapped[dict] = mapped_column(JSON)


class JobRecord(Base):
    __tablename__ = "jobs"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(100), index=True)
    payload: Mapped[dict] = mapped_column(JSON)


def init_db() -> None:
    Base.metadata.create_all(engine)
