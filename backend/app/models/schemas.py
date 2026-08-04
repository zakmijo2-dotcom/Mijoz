"""Database models for the platform."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    String, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum, 
    Integer, Float, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum


class UserRole(enum.Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class ProviderType(enum.Enum):
    """Supported AI provider types."""
    GROQ = "groq"
    OPENROUTER = "openrouter"
    GOOGLE_AI = "google_ai"
    TOGETHER_AI = "together_ai"
    CEREBRAS = "cerebras"
    MISTRAL = "mistral"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    CUSTOM = "custom"


class AgentType(enum.Enum):
    """Supported agent types."""
    CLAUDE_CODE = "claude_code"
    CODEX = "codex"
    OPENCODE = "opencode"
    PI_AGENT = "pi_agent"


class RequestStatus(enum.Enum):
    """Request status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


# Would be imported from sqlalchemy.orm import DeclarativeBase in real app
# For now, defining model classes that will work with SQLAlchemy 2.0 style

class User:
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.USER)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    api_keys: Mapped[List["ProviderApiKey"]] = relationship(back_populates="user")
    projects: Mapped[List["Project"]] = relationship(back_populates="owner")
    sessions: Mapped[List["Session"]] = relationship(back_populates="user")


class ProviderApiKey:
    """Encrypted storage for provider API keys."""
    __tablename__ = "provider_api_keys"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    provider: Mapped[ProviderType] = mapped_column(SQLEnum(ProviderType))
    name: Mapped[str] = mapped_column(String(100))  # User-friendly name
    encrypted_key: Mapped[str] = mapped_column(Text)  # Encrypted API key
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    rate_limit_per_minute: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    requests_today: Mapped[int] = mapped_column(Integer, default=0)
    last_reset: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(back_populates="api_keys")
    
    __table_args__ = (
        UniqueConstraint("user_id", "name", name="uq_user_provider_name"),
        Index("idx_provider_active", "provider", "is_active"),
    )


class Project:
    """Project model for organizing agent work."""
    __tablename__ = "projects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner: Mapped["User"] = relationship(back_populates="projects")
    sessions: Mapped[List["Session"]] = relationship(back_populates="project")


class Session:
    """Session model for agent conversations and context."""
    __tablename__ = "sessions"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType))
    name: Mapped[str] = mapped_column(String(255))
    context_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON serialized context
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project: Mapped["Project"] = relationship(back_populates="sessions")
    user: Mapped["User"] = relationship(back_populates="sessions")
    messages: Mapped[List["SessionMessage"]] = relationship(back_populates="session")
    requests: Mapped[List["ProxyRequest"]] = relationship(back_populates="session")


class SessionMessage:
    """Individual messages within a session."""
    __tablename__ = "session_messages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id"))
    role: Mapped[str] = mapped_column(String(20))  # user, assistant, system
    content: Mapped[str] = mapped_column(Text)
    metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON serialized metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session: Mapped["Session"] = relationship(back_populates="messages")


class ProxyRequest:
    """Log of proxy requests for auditing and analytics."""
    __tablename__ = "proxy_requests"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sessions.id"), nullable=True)
    provider_key_id: Mapped[int] = mapped_column(ForeignKey("provider_api_keys.id"))
    model_name: Mapped[str] = mapped_column(String(100))
    request_body: Mapped[str] = mapped_column(Text)  # JSON serialized
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON serialized
    status: Mapped[RequestStatus] = mapped_column(SQLEnum(RequestStatus))
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session: Mapped["Session"] = relationship(back_populates="requests")


class RoutingRule:
    """Routing rules for directing requests to specific providers."""
    __tablename__ = "routing_rules"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[Optional[int]] = mapped_column(ForeignKey("projects.id"), nullable=True)
    agent_type: Mapped[AgentType] = mapped_column(SQLEnum(AgentType))
    priority: Mapped[int] = mapped_column(Integer, default=0)
    preferred_providers: Mapped[str] = mapped_column(Text)  # JSON array of provider types
    fallback_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
