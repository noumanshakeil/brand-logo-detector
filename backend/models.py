from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class Brand(Base):
    __tablename__ = "brands"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    aliases_json: Mapped[str] = mapped_column(Text, default="[]")

class DetectionJob(Base):
    __tablename__ = "detection_jobs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    asset_name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(24), default="queued", index=True)
    hint_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

class MatchCandidate(Base):
    __tablename__ = "match_candidates"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    job_id: Mapped[str] = mapped_column(String(32), index=True)
    brand_id: Mapped[str] = mapped_column(String(32), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.5)
    bbox_json: Mapped[str] = mapped_column(Text, default='{"x":0.1,"y":0.2,"w":0.3,"h":0.2}')
