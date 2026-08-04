"""Provider API key management router."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.database import get_db
from app.core.security import key_encryption_service
from app.models.schemas import ProviderType
from app.routers.auth import get_current_user
from app.models.user import User
from sqlalchemy.orm import Session

router = APIRouter()


class ProviderCreate(BaseModel):
    """Request body for adding a new provider API key."""
    provider: ProviderType
    name: str = Field(..., min_length=1, max_length=100)
    api_key: str = Field(..., min_length=1)
    rate_limit_per_minute: Optional[int] = None


class ProviderResponse(BaseModel):
    """Response body for provider info (without exposing the actual key)."""
    id: int
    provider: str
    name: str
    is_active: bool
    rate_limit_per_minute: Optional[int]
    requests_today: int
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/list", response_model=List[ProviderResponse])
async def list_providers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all configured provider API keys for the current user."""
    from app.models.provider_key import ProviderKey
    
    keys = db.query(ProviderKey).filter(
        ProviderKey.user_id == current_user.id
    ).all()
    
    return keys


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_provider(
    data: ProviderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new provider API key."""
    from app.models.provider_key import ProviderKey
    
    # Check if user already has a key for this provider
    existing = db.query(ProviderKey).filter(
        ProviderKey.user_id == current_user.id,
        ProviderKey.provider == data.provider.value
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"You already have an API key for {data.provider.value}. Update it instead."
        )
    
    # Encrypt the API key before storing
    encrypted_key = key_encryption_service.encrypt(data.api_key)
    
    new_key = ProviderKey(
        user_id=current_user.id,
        provider=data.provider.value,
        name=data.name,
        encrypted_key=encrypted_key,
        rate_limit_per_minute=data.rate_limit_per_minute,
        is_active=True
    )
    
    db.add(new_key)
    db.commit()
    db.refresh(new_key)
    
    return {"message": "Provider key added successfully", "provider": data.provider.value, "id": new_key.id}


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a provider API key."""
    from app.models.provider_key import ProviderKey
    
    key = db.query(ProviderKey).filter(
        ProviderKey.id == provider_id,
        ProviderKey.user_id == current_user.id
    ).first()
    
    if not key:
        raise HTTPException(status_code=404, detail="Provider key not found")
    
    db.delete(key)
    db.commit()
    
    return {"message": "Provider key deleted successfully"}


@router.put("/{provider_id}/toggle")
async def toggle_provider(
    provider_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle a provider API key active/inactive."""
    from app.models.provider_key import ProviderKey
    
    key = db.query(ProviderKey).filter(
        ProviderKey.id == provider_id,
        ProviderKey.user_id == current_user.id
    ).first()
    
    if not key:
        raise HTTPException(status_code=404, detail="Provider key not found")
    
    key.is_active = not key.is_active
    db.commit()
    
    return {"message": "Provider key toggled successfully", "is_active": key.is_active}


@router.get("/usage")
async def get_usage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get usage statistics for all provider keys."""
    from app.models.provider_key import ProviderKey
    
    keys = db.query(ProviderKey).filter(
        ProviderKey.user_id == current_user.id
    ).all()
    
    total_requests = sum(k.requests_today for k in keys)
    by_provider = {k.provider: k.requests_today for k in keys}
    
    return {
        "total_requests": total_requests,
        "by_provider": by_provider,
        "today_requests": total_requests,
    }
