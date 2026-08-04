"""
Mijoz - AI Engineering Operating System
Agent and Model Router Implementation
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import asyncio
import time


class AgentRole(str, Enum):
    """Available agent roles in the system"""
    ARCHITECT = "architect"
    DEVELOPER = "developer"
    DEBUGGER = "debugger"
    TESTER = "tester"
    REVIEWER = "reviewer"
    SECURITY_AUDITOR = "security_auditor"
    DOCUMENTATION = "documentation"
    DEVOPS = "devops"


class ModelProvider(str, Enum):
    """Supported model providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    GROQ = "groq"
    OPENROUTER = "openrouter"
    TOGETHER = "together"
    CEREBRAS = "cerebras"
    MISTRAL = "mistral"
    LOCAL = "local"


class TaskType(str, Enum):
    """Types of tasks for routing decisions"""
    ARCHITECTURE = "architecture"
    CODING = "coding"
    DEBUGGING = "debugging"
    TESTING = "testing"
    REVIEW = "review"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    DEVOPS = "devops"
    REFACTORING = "refactoring"
    QUICK_FIX = "quick_fix"


class RoutingStrategy(str, Enum):
    """Strategies for model routing"""
    COST_OPTIMIZED = "cost_optimized"
    SPEED_OPTIMIZED = "speed_optimized"
    QUALITY_OPTIMIZED = "quality_optimized"
    BALANCED = "balanced"
    CONTEXT_AWARE = "context_aware"


class AgentConfig(BaseModel):
    """Configuration for an agent"""
    name: str
    role: AgentRole
    system_prompt: str
    allowed_tools: List[str] = []
    permissions: Dict[str, bool] = Field(default_factory=lambda: {
        "read_files": True,
        "write_files": False,
        "execute_commands": False,
        "access_git": False,
        "access_network": False,
        "access_browser": False
    })
    default_model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 4096
    temperature: float = 0.7
    budget_limit: Optional[float] = None
    context_window: int = 8192


class ModelConfig(BaseModel):
    """Configuration for a model"""
    provider: ModelProvider
    model_name: str
    api_key_env: str
    base_url: Optional[str] = None
    cost_per_million_input: float = 0.0
    cost_per_million_output: float = 0.0
    max_tokens: int = 4096
    context_window: int = 8192
    speed_tier: int = 1  # 1=fastest, 5=slowest
    quality_tier: int = 1  # 1=highest, 5=lowest
    supports_function_calling: bool = True
    is_available: bool = True


class RoutingDecision(BaseModel):
    """Result of a routing decision"""
    selected_agent: Optional[str] = None
    selected_model: str
    selected_provider: ModelProvider
    reasoning: str
    estimated_cost: float = 0.0
    estimated_time: float = 0.0
    fallback_options: List[str] = []


class TaskContext(BaseModel):
    """Context for a task being routed"""
    task_id: str
    task_type: TaskType
    description: str
    complexity: int = Field(ge=1, le=5, default=3)  # 1=simple, 5=complex
    urgency: int = Field(ge=1, le=5, default=3)  # 1=low, 5=critical
    budget_sensitivity: int = Field(ge=1, le=5, default=3)
    required_context: int = 0  # tokens needed
    project_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    """Current state of an agent"""
    agent_id: str
    role: AgentRole
    status: str = "idle"  # idle, busy, error
    current_task: Optional[str] = None
    progress: float = 0.0
    last_active: float = Field(default_factory=time.time)
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0


class ModelHealth(BaseModel):
    """Health status of a model/provider"""
    provider: ModelProvider
    model_name: str
    is_healthy: bool = True
    last_check: float = Field(default_factory=time.time)
    response_time_avg: float = 0.0
    success_rate: float = 1.0
    rate_limit_remaining: Optional[int] = None
    quota_remaining: Optional[float] = None
    error_count: int = 0
    last_error: Optional[str] = None
