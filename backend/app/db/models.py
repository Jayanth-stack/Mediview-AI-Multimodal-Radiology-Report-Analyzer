from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


class Study(Base):
    __tablename__ = "studies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[str] = mapped_column(String(64), index=True)
    modality: Mapped[str] = mapped_column(String(32))
    image_s3_key: Mapped[str] = mapped_column(String(256))

    reports: Mapped[list["Report"]] = relationship("Report", back_populates="study")
    findings: Mapped[list["Finding"]] = relationship("Finding", back_populates="study")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"))
    text: Mapped[str] = mapped_column(String(4000))

    study: Mapped["Study"] = relationship("Study", back_populates="reports")


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    study_id: Mapped[int] = mapped_column(ForeignKey("studies.id"))
    label: Mapped[str] = mapped_column(String(128))
    confidence: Mapped[float] = mapped_column(Float)

    study: Mapped["Study"] = relationship("Study", back_populates="findings")

