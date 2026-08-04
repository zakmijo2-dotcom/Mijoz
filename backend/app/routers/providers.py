"""Provider API key management router."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

from app.core.security import key_encryption_service
from app.models.schemas import ProviderType
from app.routers.auth import get_current_user

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


@router.get("/list", response_model=List[ProviderResponse])
async def list_providers(current_user: dict = Depends(get_current_user)):
    """List all configured provider API keys for the current user."""
    # Placeholder - would fetch from database
    # keys = db.query(ProviderApiKey).filter_by(user_id=current_user["id"]).all()
    return []


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_provider(
    data: ProviderCreate,
    current_user: dict = Depends(get_current_user),
):
    """Add a new provider API key."""
    # Encrypt the API key before storing
    encrypted_key = key_encryption_service.encrypt(data.api_key)
    
    # Placeholder - would save to database
    # new_key = ProviderApiKey(
    #     user_id=current_user["id"],
    #     provider=data.provider,
    #     name=data.name,
    #     encrypted_key=encrypted_key,
    #     rate_limit_per_minute=data.rate_limit_per_minute,
    # )
    # db.add(new_key)
    # db.commit()
    
    return {"message": "Provider key added successfully", "provider": data.provider.value}


@router.delete("/{provider_id}")
async def delete_provider(
    provider_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Delete a provider API key."""
    # Placeholder - would delete from database
    # key = db.query(ProviderApiKey).filter_by(id=provider_id, user_id=current_user["id"]).first()
    # if not key:
    #     raise HTTPException(status_code=404, detail="Provider key not found")
    # db.delete(key)
    # db.commit()
    
    return {"message": "Provider key deleted successfully"}


@router.put("/{provider_id}/toggle")
async def toggle_provider(
    provider_id: int,
    current_user: dict = Depends(get_current_user),
):
    """Toggle a provider API key active/inactive."""
    # Placeholder - would update in database
    # key = db.query(ProviderApiKey).filter_by(id=provider_id, user_id=current_user["id"]).first()
    # if not key:
    #     raise HTTPException(status_code=404, detail="Provider key not found")
    # key.is_active = not key.is_active
    # db.commit()
    
    return {"message": "Provider key toggled successfully"}


@router.get("/usage")
async def get_usage(current_user: dict = Depends(get_current_user)):
    """Get usage statistics for all provider keys."""
    # Placeholder - would aggregate from proxy_requests table
    return {
        "total_requests": 0,
        "by_provider": {},
        "today_requests": 0,
    }
