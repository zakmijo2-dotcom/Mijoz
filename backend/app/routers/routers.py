"""
API Routers for Agent and Model Router endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..services.agent_router import agent_router, AgentRouter
from ..services.model_router import model_router, ModelRouter
from ..models.router_models import (
    TaskContext, TaskType, RoutingStrategy, AgentRole,
    AgentConfig, ModelProvider
)

router = APIRouter(prefix="/api/v1", tags=["routers"])


# ============== Agent Router Endpoints ==============

class CreateAgentRequest(BaseModel):
    name: str
    role: AgentRole
    system_prompt: str
    default_model: str = "claude-sonnet-4-20250514"
    allowed_tools: List[str] = []
    permissions: Dict[str, bool] = {}


@router.get("/agents")
async def get_agents(role: Optional[AgentRole] = None):
    """Get all available agents"""
    return {"agents": agent_router.get_available_agents(role)}


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""
    agent = agent_router.get_agent_by_id(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/agents")
async def create_agent(request: CreateAgentRequest):
    """Create a custom agent"""
    config = AgentConfig(
        name=request.name,
        role=request.role,
        system_prompt=request.system_prompt,
        default_model=request.default_model,
        allowed_tools=request.allowed_tools,
        permissions=request.permissions or {
            "read_files": True,
            "write_files": False,
            "execute_commands": False,
            "access_git": False,
            "access_network": False,
            "access_browser": False
        }
    )
    
    agent_id = agent_router.register_agent(config)
    return {"agent_id": agent_id, "status": "created"}


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str):
    """Delete an agent"""
    agent_router.unregister_agent(agent_id)
    return {"status": "deleted"}


@router.get("/agents/stats")
async def get_agent_stats():
    """Get dashboard statistics for agents"""
    return agent_router.get_dashboard_stats()


@router.get("/agents/active-tasks")
async def get_active_tasks():
    """Get all currently active tasks"""
    return {"tasks": agent_router.get_active_tasks()}


@router.get("/agents/history")
async def get_task_history(
    limit: int = 100,
    agent_id: Optional[str] = None
):
    """Get task history"""
    return {"history": agent_router.get_task_history(limit, agent_id)}


@router.post("/tasks/route")
async def route_task(task_context: TaskContext):
    """Route a task to the appropriate agent"""
    agent_id = await agent_router.route_task(task_context)
    
    if not agent_id:
        raise HTTPException(
            status_code=503,
            detail="No available agents for this task type"
        )
    
    return {
        "task_id": task_context.task_id,
        "assigned_agent": agent_id,
        "status": "queued"
    }


@router.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    success: bool,
    result: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
):
    """Mark a task as complete"""
    await agent_router.complete_task(task_id, success, result, error)
    return {"status": "completed"}


@router.post("/tasks/{task_id}/progress")
async def update_progress(
    task_id: str,
    agent_id: str,
    progress: float
):
    """Update task progress"""
    await agent_router.update_agent_progress(agent_id, task_id, progress)
    return {"status": "updated", "progress": progress}


# ============== Model Router Endpoints ==============

@router.get("/models")
async def get_models(
    provider: Optional[ModelProvider] = None,
    only_healthy: bool = True
):
    """Get all available models"""
    return {"models": model_router.get_available_models(provider, only_healthy)}


@router.get("/models/stats")
async def get_model_stats():
    """Get usage statistics for all models"""
    return model_router.get_usage_stats()


@router.post("/models/route")
async def route_to_model(
    task_context: TaskContext,
    strategy: RoutingStrategy = RoutingStrategy.BALANCED,
    excluded_models: Optional[List[str]] = None
):
    """Route a task to the optimal model"""
    decision = await model_router.route_task(
        task_context,
        strategy,
        excluded_models
    )
    
    if not decision.selected_model:
        raise HTTPException(
            status_code=503,
            detail="No available models found"
        )
    
    return decision.dict()


@router.post("/models/{provider}/{model_name}/health")
async def update_model_health(
    provider: ModelProvider,
    model_name: str,
    success: bool,
    response_time: float,
    error_message: Optional[str] = None
):
    """Update model health status"""
    await model_router.update_health(
        provider,
        model_name,
        success,
        response_time,
        error_message
    )
    return {"status": "updated"}


# ============== Pipeline Endpoints ==============

class CreatePipelineRequest(BaseModel):
    task_description: str
    pipeline_roles: List[AgentRole]


@router.post("/pipelines")
async def create_pipeline(request: CreatePipelineRequest):
    """Create an agent pipeline for complex tasks"""
    pipeline = agent_router.create_agent_pipeline(
        request.task_description,
        request.pipeline_roles
    )
    return pipeline


@router.post("/pipelines/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str,
    initial_context: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Execute an agent pipeline"""
    # Find pipeline (in production, store in database)
    # For now, this is a simplified version
    
    return {
        "pipeline_id": pipeline_id,
        "status": "executing",
        "message": "Pipeline execution started"
    }
