"""Sessions router for managing agent sessions."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models.schemas import AgentType
from app.routers.auth import get_current_user

router = APIRouter()


class SessionCreate(BaseModel):
    """Request body for creating a session."""
    project_id: int
    agent_type: AgentType
    name: str = Field(..., min_length=1, max_length=255)


class SessionMessage(BaseModel):
    """Request body for adding a message to a session."""
    role: str  # user, assistant, system
    content: str


class SessionResponse(BaseModel):
    """Response body for session data."""
    id: int
    project_id: int
    agent_type: str
    name: str
    is_active: bool
    created_at: str
    updated_at: str
    message_count: int = 0


@router.get("/list", response_model=List[SessionResponse])
async def list_sessions(
    project_id: Optional[int] = None,
    current_user: dict = Depends(get_current_user),
):
    """List all sessions for the current user, optionally filtered by project."""
    # Placeholder - would fetch from database
    return []


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_session(
    data: SessionCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new session for an agent."""
    # Placeholder - would save to database
    return {
        "id": 1,
        "project_id": data.project_id,
        "agent_type": data.agent_type.value,
        "name": data.name,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "message_count": 0,
    }


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific session by ID."""
    # Placeholder - would fetch from database
    raise HTTPException(status_code=404, detail="Session not found")


@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: int,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    """Get messages for a session."""
    # Placeholder - would fetch from database
    return {"messages": []}


@router.post("/{session_id}/messages")
async def add_session_message(
    session_id: int,
    data: SessionMessage,
    current_user: dict = Depends(get_current_user),
):
    """Add a message to a session."""
    # Placeholder - would save to database
    return {"message": "Message added successfully"}


@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Delete/close a session (soft delete)."""
    # Placeholder - would soft delete in database
    return {"message": "Session deleted successfully"}


@router.post("/{session_id}/switch-agent")
async def switch_agent(
    session_id: int,
    agent_type: AgentType,
    current_user: dict = Depends(get_current_user),
):
    """Switch the agent type for a session while preserving context."""
    # Placeholder - would update session and migrate context if needed
    return {
        "message": "Agent switched successfully",
        "new_agent": agent_type.value,
    }
