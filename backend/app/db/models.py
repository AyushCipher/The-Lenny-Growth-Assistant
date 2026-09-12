import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="New Strategy Chat")
    user_metadata = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.timestamp")
    artifacts = relationship("ArtifactModel", back_populates="session", cascade="all, delete-orphan", order_by="ArtifactModel.created_at")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # user | assistant | system
    content = Column(Text, nullable=False)
    citations = Column(JSON, nullable=True, default=list)  # List of source references
    model_used = Column(String(100), nullable=True)
    latency_ms = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("SessionModel", back_populates="messages")


class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(String(36), nullable=True)
    title = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # markdown | html
    content = Column(Text, nullable=False)
    sanitized_content = Column(Text, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    session = relationship("SessionModel", back_populates="artifacts")


class SourceModel(Base):
    __tablename__ = "sources"

    id = Column(String(100), primary_key=True)  # e.g. src_shreyas_doshi_01
    source_reference = Column(String(255), nullable=False)
    episode_id = Column(String(50), nullable=False)
    episode_title = Column(String(255), nullable=False)
    guest = Column(String(100), nullable=False)
    topic = Column(String(255), nullable=False)
    timestamp_str = Column(String(50), nullable=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True, default=dict)


class SystemMetricModel(Base):
    __tablename__ = "system_metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    request_id = Column(String(64), nullable=False)
    endpoint = Column(String(100), nullable=False)
    provider = Column(String(50), nullable=False)
    model = Column(String(100), nullable=False)
    input_tokens = Column(Integer, nullable=True)
    output_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    retrieval_count = Column(Integer, nullable=False, default=0)
    retrieval_ms = Column(Float, nullable=False, default=0.0)
    llm_ms = Column(Float, nullable=False, default=0.0)
    total_ms = Column(Float, nullable=False, default=0.0)
    status = Column(String(50), nullable=False)  # success | error
    timestamp = Column(DateTime(timezone=True), default=utcnow, nullable=False)
