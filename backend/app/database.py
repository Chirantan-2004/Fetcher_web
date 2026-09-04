from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4
from sqlalchemy import DateTime, JSON, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker
from app.config import get_settings

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
class Base(DeclarativeBase): pass
class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_url: Mapped[str] = mapped_column(String(2048)); status: Mapped[str] = mapped_column(String(32), default="queued")
    progress: Mapped[int] = mapped_column(default=0); created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    document_json: Mapped[dict] = mapped_column(JSON, nullable=True); files: Mapped[dict] = mapped_column(JSON, nullable=True); error: Mapped[dict] = mapped_column(JSON, nullable=True)
def init_db() -> None:
    Path(settings.storage_path).mkdir(parents=True, exist_ok=True); Base.metadata.create_all(engine)
def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()
