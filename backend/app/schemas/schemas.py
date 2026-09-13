from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# Token Usage Schema
class TokenUsage(BaseModel):
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


# Citation Schema
class Citation(BaseModel):
    source_id: str
    source_reference: str
    episode_id: str
    episode_title: str
    guest: str
    topic: str
    timestamp_str: Optional[str] = None
    snippet: str


# Artifact Schema
class ArtifactBase(BaseModel):
    title: str
    type: str  # markdown | html
    content: str
    sanitized_content: str
    version: int = 1


class ArtifactResponse(ArtifactBase):
    id: str
    session_id: str
    message_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Chat Schemas
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=10000, description="User query prompt")
    session_id: Optional[str] = Field(None, description="Existing session UUID, or null to create one")
    provider: Optional[str] = Field(None, description="ollama | anthropic | openai")
    model: Optional[str] = Field(None, description="Model identifier override")
    user_metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str = "assistant"
    content: str
    citations: list[Citation] = Field(default_factory=list)
    artifacts: list[ArtifactResponse] = Field(default_factory=list)
    provider: str
    model: str
    latency_ms: float
    token_usage: Optional[TokenUsage] = None


# Ship 30 for 30 Skill Schemas
class Ship30Request(BaseModel):
    topic: str = Field(..., min_length=3, max_length=500, description="Core essay topic or contrarian viewpoint")
    target_audience: Optional[str] = Field("Product Managers & Growth Leaders", description="Target reader persona")
    core_takeaway: Optional[str] = Field(None, description="Key action or lesson reader should implement")
    guest_focus: Optional[str] = Field(None, description="Specific Lenny guest influence (e.g. Shreyas Doshi, Elena Verna)")
    session_id: Optional[str] = None
    provider: Optional[str] = None


class Ship30Response(BaseModel):
    session_id: str
    message_id: str
    title: str
    essay_markdown: str
    word_count: int
    citations: list[Citation] = Field(default_factory=list)
    provider: str
    model: str
    latency_ms: float
    token_usage: Optional[TokenUsage] = None


# Session Schemas
class SessionCreate(BaseModel):
    title: Optional[str] = "New Strategy Chat"
    user_metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    id: str
    title: str
    user_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    artifact_count: int = 0

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    model_used: Optional[str] = None
    latency_ms: Optional[float] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class SessionDetailResponse(BaseModel):
    id: str
    title: str
    user_metadata: Optional[dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    messages: list[MessageResponse] = Field(default_factory=list)
    artifacts: list[ArtifactResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True


# Source Schemas
class SourceResponse(BaseModel):
    id: str
    source_reference: str
    episode_id: str
    episode_title: str
    guest: str
    topic: str
    timestamp_str: Optional[str] = None
    content: str
    metadata_json: Optional[dict[str, Any]] = None

    class Config:
        from_attributes = True


# Model Provider Status Schemas
class ModelInfo(BaseModel):
    provider: str  # ollama | anthropic | openai
    model_name: str
    display_name: str
    is_available: bool
    status_message: str
    is_active: bool


class ModelListResponse(BaseModel):
    active_provider: str
    active_model: str
    models: list[ModelInfo]


class ModelSelectRequest(BaseModel):
    provider: str
    model: Optional[str] = None


# Diagnostics & Health Schemas
class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str
    environment: str
    database: str
    timestamp: datetime


class DiagnosticsResponse(BaseModel):
    status: str
    uptime_seconds: float
    database_connected: bool
    database_latency_ms: float
    ollama_connected: bool
    ollama_models: list[str]
    anthropic_configured: bool
    openai_configured: bool
    groq_configured: bool = False
    indexed_episodes: int
    indexed_chunks: int
    index_version: str
    recent_latencies_p95_ms: float
    recent_requests_count: int


# RFC-7807 Standard Error Response
class ErrorDetail(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: Optional[str] = None
