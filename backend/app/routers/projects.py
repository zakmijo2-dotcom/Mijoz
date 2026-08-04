"""Projects router for managing user projects."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.routers.auth import get_current_user

router = APIRouter()


class ProjectCreate(BaseModel):
    """Request body for creating a project."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    """Response body for project data."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    session_count: int = 0


@router.get("/list", response_model=List[ProjectResponse])
async def list_projects(current_user: dict = Depends(get_current_user)):
    """List all projects for the current user."""
    # Placeholder - would fetch from database
    return []


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create a new project."""
    # Placeholder - would save to database
    return {
        "id": 1,
        "name": data.name,
        "description": data.description,
        "is_active": True,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "session_count": 0,
    }


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Get a specific project by ID."""
    # Placeholder - would fetch from database
    raise HTTPException(status_code=404, detail="Project not found")


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    data: ProjectCreate,
    current_user: dict = Depends(get_current_user),
):
    """Update a project."""
    # Placeholder - would update in database
    return {"message": "Project updated successfully"}


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Delete a project (soft delete)."""
    # Placeholder - would soft delete in database
    return {"message": "Project deleted successfully"}
