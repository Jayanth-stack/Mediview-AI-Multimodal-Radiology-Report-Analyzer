from typing import Optional
from sqlalchemy import String, Integer, Float, ForeignKey, Enum, JSON, DateTime, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
import enum
from datetime import datetime

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None  # Fallback if pgvector not installed


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False)


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    modality: Mapped[str] = mapped_column(String(32))
    image_s3_key: Mapped[str] = mapped_column(String(256))
    source : Mapped[str] = mapped_column(String(128), default = 'upload')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    patient_context : Mapped[Optional[str]] = mapped_column(String(4000), nullable = True)


    reports: Mapped[list["Report"]] = relationship("Report", back_populates="study")
    findings: Mapped[list["Finding"]] = relationship("Finding", back_populates="study")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"))
    text: Mapped[str] = mapped_column(String(4000))
    summary_model : Mapped[Optional[str]] = mapped_column(String(128), nullable = True)

    study: Mapped["Study"] = relationship("Study", back_populates="reports")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"))
    label: Mapped[str] = mapped_column(String(128))
    confidence: Mapped[float] = mapped_column(Float)
    model_name: Mapped[Optional[str]] = mapped_column(String(128), nullable = True)
    model_version: Mapped[Optional[str]] = mapped_column(String(128), nullable = True)
    extra: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    study: Mapped["Study"] = relationship("Study", back_populates="findings")


class JobStatusEnum(str, enum.Enum):
    queued = "queued"
    running = "running"
    completed = "completed"
    failed = "failed"


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(32), default="analyze")
    status: Mapped[str] = mapped_column(String(16), default=JobStatusEnum.queued.value)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    s3_key: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)


class Document(Base):
    """Document model for RAG knowledge base with vector embeddings."""
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(200), index=True)  # e.g., "radiopaedia", "acr"
    doc_type: Mapped[str] = mapped_column(String(50), index=True)  # e.g., "guideline", "case"
    embedding = mapped_column(Vector(768) if Vector else Text, nullable=True)  # 768 dims for Gemini embeddings
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

