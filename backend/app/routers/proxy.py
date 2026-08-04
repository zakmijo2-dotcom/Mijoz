"""Proxy endpoint for routing AI requests through configured providers."""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import structlog

from app.services.proxy import proxy_service
from app.models.schemas import AgentType
from app.routers.auth import get_current_user

logger = structlog.get_logger()
router = APIRouter()


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str  # system, user, assistant
    content: str


class ProxyRequest(BaseModel):
    """Request body for proxying an AI request."""
    messages: List[ChatMessage]
    model: str = Field(default="llama-3.1-70b-versatile")
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=1)
    stream: bool = False
    agent_type: Optional[AgentType] = None
    preferred_providers: Optional[List[str]] = None


class ProxyResponse(BaseModel):
    """Response from the proxy service."""
    id: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]]
    model: str
    used_provider: str
    latency_ms: int
    retries: int


@router.post("/chat", response_model=ProxyResponse)
async def chat_completion(
    request: ProxyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a chat completion request through the proxy layer.
    
    The proxy will automatically route through available providers with fallback.
    """
    # Placeholder - would fetch user's available provider keys from DB
    # available_keys = db.query(ProviderApiKey).filter_by(
    #     user_id=current_user["id"], is_active=True
    # ).all()
    
    # For demo, return error if no keys configured
    available_keys = []  # Would be populated from database
    
    if not available_keys:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No provider API keys configured. Please add keys in the Providers section.",
        )
    
    # Build standard request body
    request_body = {
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }
    
    try:
        # Route with automatic fallback
        response = await proxy_service.route_with_fallback(
            available_keys=available_keys,
            request_body=request_body,
            preferred_model=request.model,
            agent_type=request.agent_type,
        )
        
        logger.info(
            "proxy_request_completed",
            user_email=current_user.get("email"),
            provider=response.get("used_provider"),
            latency_ms=response.get("latency_ms"),
        )
        
        return response
        
    except Exception as e:
        logger.error("proxy_request_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"All providers failed: {str(e)}",
        )


@router.post("/chat/stream")
async def chat_completion_stream(
    request: ProxyRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Send a streaming chat completion request.
    
    Returns Server-Sent Events (SSE) stream.
    """
    from fastapi.responses import StreamingResponse
    
    # Placeholder - would fetch user's preferred provider
    preferred_provider = None  # Would be determined from routing rules
    
    if not preferred_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No provider API keys configured.",
        )
    
    request_body = {
        "messages": [{"role": m.role, "content": m.content} for m in request.messages],
        "temperature": request.temperature,
        "max_tokens": request.max_tokens,
    }
    
    async def generate():
        try:
            # In real implementation, would decrypt key and stream
            # api_key = key_encryption_service.decrypt(preferred_provider.encrypted_key)
            # async for chunk in proxy_service.stream_request(...):
            #     yield f"data: {chunk}\n\n"
            pass
        except Exception as e:
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
        finally:
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
