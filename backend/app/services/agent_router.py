"""
Agent Router - Intelligent routing of tasks to specialized AI agents
"""

from typing import Dict, List, Optional, Any
import asyncio
import time
import uuid
from datetime import datetime
from app.models.router_models import (
    AgentConfig, AgentRole, TaskContext, TaskType,
    AgentState, ModelProvider
)


class AgentRouter:
    """
    Intelligent agent router that distributes tasks to specialized agents
    and manages agent-to-agent communication.
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self.agent_states: Dict[str, AgentState] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        self._lock = asyncio.Lock()
        
        # Initialize default agents
        self._register_default_agents()
    
    def _register_default_agents(self):
        """Register default agent configurations"""
        defaults = [
            AgentConfig(
                name="Architect",
                role=AgentRole.ARCHITECT,
                system_prompt="""You are an expert software architect. Your role is to:
- Analyze requirements and design system architecture
- Create technical specifications and documentation
- Define project structure and patterns
- Make high-level technology decisions
- Review and approve architectural changes

Always think systematically and consider scalability, maintainability, and best practices.""",
                allowed_tools=["read_files", "write_files", "search_code"],
                permissions={
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": False,
                    "access_git": True,
                    "access_network": False,
                    "access_browser": False
                },
                default_model="claude-opus-4-20250514",
                max_tokens=8192,
                temperature=0.7,
                budget_limit=10.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="Developer",
                role=AgentRole.DEVELOPER,
                system_prompt="""You are a senior full-stack developer. Your role is to:
- Implement features based on specifications
- Write clean, efficient, and well-documented code
- Follow coding standards and best practices
- Refactor existing code when needed
- Fix bugs and issues

Always write testable code and include appropriate error handling.""",
                allowed_tools=["read_files", "write_files", "execute_commands", "search_code"],
                permissions={
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": True,
                    "access_git": True,
                    "access_network": False,
                    "access_browser": False
                },
                default_model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.7,
                budget_limit=5.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="Debugger",
                role=AgentRole.DEBUGGER,
                system_prompt="""You are an expert debugger. Your role is to:
- Analyze error messages and stack traces
- Identify root causes of bugs
- Propose and implement fixes
- Test fixes thoroughly
- Document the debugging process

Always approach problems methodically and verify fixes completely.""",
                allowed_tools=["read_files", "write_files", "execute_commands", "search_code"],
                permissions={
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": True,
                    "access_git": False,
                    "access_network": False,
                    "access_browser": False
                },
                default_model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.3,
                budget_limit=5.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="Tester",
                role=AgentRole.TESTER,
                system_prompt="""You are a QA engineer and testing expert. Your role is to:
- Write comprehensive test suites
- Execute tests and analyze results
- Identify edge cases and potential issues
- Ensure code coverage
- Validate functionality against requirements

Always be thorough and think like both a user and an attacker.""",
                allowed_tools=["read_files", "write_files", "execute_commands", "search_code"],
                permissions={
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": True,
                    "access_git": True,
                    "access_network": False,
                    "access_browser": False
                },
                default_model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.5,
                budget_limit=5.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="Reviewer",
                role=AgentRole.REVIEWER,
                system_prompt="""You are a senior code reviewer. Your role is to:
- Review code for quality, correctness, and best practices
- Check for security vulnerabilities
- Ensure code follows project conventions
- Suggest improvements and optimizations
- Approve or request changes

Always provide constructive feedback and explain your reasoning.""",
                allowed_tools=["read_files", "search_code"],
                permissions={
                    "read_files": True,
                    "write_files": False,
                    "execute_commands": False,
                    "access_git": True,
                    "access_network": False,
                    "access_browser": False
                },
                default_model="claude-opus-4-20250514",
                max_tokens=8192,
                temperature=0.3,
                budget_limit=5.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="Security Auditor",
                role=AgentRole.SECURITY_AUDITOR,
                system_prompt="""You are a security expert and auditor. Your role is to:
- Identify security vulnerabilities
- Review authentication and authorization
- Check for common security issues (OWASP Top 10)
- Audit dependencies for known vulnerabilities
- Recommend security improvements

Always think like an attacker and be thorough in your analysis.""",
                allowed_tools=["read_files", "search_code", "scan_dependencies"],
                permissions={
                    "read_files": True,
                    "write_files": False,
                    "execute_commands": True,
                    "access_git": False,
                    "access_network": True,
                    "access_browser": False
                },
                default_model="claude-opus-4-20250514",
                max_tokens=8192,
                temperature=0.3,
                budget_limit=10.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="Documentation",
                role=AgentRole.DOCUMENTATION,
                system_prompt="""You are a technical writer. Your role is to:
- Write clear and comprehensive documentation
- Create API documentation
- Write README files and guides
- Document code with inline comments
- Maintain changelogs

Always write for your audience and keep documentation up to date.""",
                allowed_tools=["read_files", "write_files"],
                permissions={
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": False,
                    "access_git": True,
                    "access_network": False,
                    "access_browser": False
                },
                default_model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.7,
                budget_limit=3.0,
                context_window=200000
            ),
            
            AgentConfig(
                name="DevOps",
                role=AgentRole.DEVOPS,
                system_prompt="""You are a DevOps engineer. Your role is to:
- Manage CI/CD pipelines
- Configure deployment environments
- Optimize build processes
- Monitor system health
- Handle infrastructure as code

Always prioritize reliability, security, and automation.""",
                allowed_tools=["read_files", "write_files", "execute_commands", "access_git"],
                permissions={
                    "read_files": True,
                    "write_files": True,
                    "execute_commands": True,
                    "access_git": True,
                    "access_network": True,
                    "access_browser": False
                },
                default_model="claude-sonnet-4-20250514",
                max_tokens=4096,
                temperature=0.5,
                budget_limit=5.0,
                context_window=200000
            ),
        ]
        
        for agent in defaults:
            agent_id = f"{agent.role.value}-{uuid.uuid4().hex[:8]}"
            self.agents[agent_id] = agent
            self.agent_states[agent_id] = AgentState(
                agent_id=agent_id,
                role=agent.role,
                status="idle"
            )
    
    def register_agent(self, config: AgentConfig) -> str:
        """Register a custom agent"""
        agent_id = f"{config.role.value}-{uuid.uuid4().hex[:8]}"
        self.agents[agent_id] = config
        self.agent_states[agent_id] = AgentState(
            agent_id=agent_id,
            role=config.role,
            status="idle"
        )
        return agent_id
    
    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id in self.agents:
            del self.agents[agent_id]
        if agent_id in self.agent_states:
            del self.agent_states[agent_id]
    
    async def route_task(
        self,
        task_context: TaskContext,
        preferred_agents: Optional[List[AgentRole]] = None
    ) -> Optional[str]:
        """
        Route a task to the most appropriate agent.
        Returns the agent_id or None if no suitable agent found.
        """
        async with self._lock:
            # Map task types to preferred agent roles
            task_role_mapping = {
                TaskType.ARCHITECTURE: AgentRole.ARCHITECT,
                TaskType.CODING: AgentRole.DEVELOPER,
                TaskType.DEBUGGING: AgentRole.DEBUGGER,
                TaskType.TESTING: AgentRole.TESTER,
                TaskType.REVIEW: AgentRole.REVIEWER,
                TaskType.SECURITY: AgentRole.SECURITY_AUDITOR,
                TaskType.DOCUMENTATION: AgentRole.DOCUMENTATION,
                TaskType.DEVOPS: AgentRole.DEVOPS,
                TaskType.REFACTORING: AgentRole.DEVELOPER,
                TaskType.QUICK_FIX: AgentRole.DEBUGGER,
            }
            
            # Determine required role
            required_role = task_role_mapping.get(task_context.task_type)
            
            if not required_role:
                # Default to developer for unknown task types
                required_role = AgentRole.DEVELOPER
            
            # Find available agents with the required role
            candidates = []
            for agent_id, agent in self.agents.items():
                if agent.role != required_role:
                    continue
                
                # Skip if agent is busy
                state = self.agent_states.get(agent_id)
                if state and state.status == "busy":
                    continue
                
                # Skip if agent is in error state
                if state and state.status == "error":
                    continue
                
                candidates.append((agent_id, agent, state))
            
            if not candidates:
                # No idle agents, find the least busy one
                for agent_id, agent in self.agents.items():
                    if agent.role == required_role:
                        state = self.agent_states.get(agent_id)
                        if state:
                            candidates.append((agent_id, agent, state))
                
                if candidates:
                    # Sort by progress (lowest first)
                    candidates.sort(key=lambda x: x[2].progress if x[2] else 0)
            
            if not candidates:
                return None
            
            # Select the best candidate
            selected_id, selected_agent, selected_state = candidates[0]
            
            # Update agent state
            if selected_state:
                selected_state.status = "busy"
                selected_state.current_task = task_context.task_id
                selected_state.total_tasks += 1
            
            # Record active task
            self.active_tasks[task_context.task_id] = {
                "agent_id": selected_id,
                "agent_role": selected_agent.role,
                "task_context": task_context,
                "started_at": time.time(),
                "status": "running"
            }
            
            return selected_id
    
    async def complete_task(
        self,
        task_id: str,
        success: bool,
        result: Optional[Any] = None,
        error: Optional[str] = None
    ):
        """Mark a task as complete"""
        async with self._lock:
            if task_id not in self.active_tasks:
                return
            
            task_info = self.active_tasks[task_id]
            agent_id = task_info["agent_id"]
            
            # Update agent state
            if agent_id in self.agent_states:
                state = self.agent_states[agent_id]
                state.status = "idle"
                state.current_task = None
                state.progress = 0.0
                if success:
                    state.successful_tasks += 1
                else:
                    state.failed_tasks += 1
            
            # Record task history
            self.task_history.append({
                "task_id": task_id,
                "agent_id": agent_id,
                "success": success,
                "result": result,
                "error": error,
                "started_at": task_info["started_at"],
                "completed_at": time.time()
            })
            
            # Remove from active tasks
            del self.active_tasks[task_id]
    
    async def update_agent_progress(
        self,
        agent_id: str,
        task_id: str,
        progress: float
    ):
        """Update the progress of an agent's current task"""
        async with self._lock:
            if agent_id in self.agent_states:
                state = self.agent_states[agent_id]
                if state.current_task == task_id:
                    state.progress = min(100.0, max(0.0, progress))
                    state.last_active = time.time()
    
    def get_available_agents(
        self,
        role: Optional[AgentRole] = None
    ) -> List[Dict[str, Any]]:
        """Get list of available agents"""
        results = []
        
        for agent_id, agent in self.agents.items():
            state = self.agent_states.get(agent_id)
            
            if role and agent.role != role:
                continue
            
            results.append({
                "agent_id": agent_id,
                "name": agent.name,
                "role": agent.role.value,
                "status": state.status if state else "unknown",
                "current_task": state.current_task if state else None,
                "progress": state.progress if state else 0.0,
                "total_tasks": state.total_tasks if state else 0,
                "successful_tasks": state.successful_tasks if state else 0,
                "failed_tasks": state.failed_tasks if state else 0,
                "permissions": agent.permissions,
                "default_model": agent.default_model
            })
        
        return results
    
    def get_agent_by_id(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific agent"""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        state = self.agent_states.get(agent_id)
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "role": agent.role.value,
            "system_prompt": agent.system_prompt,
            "allowed_tools": agent.allowed_tools,
            "permissions": agent.permissions,
            "default_model": agent.default_model,
            "max_tokens": agent.max_tokens,
            "temperature": agent.temperature,
            "budget_limit": agent.budget_limit,
            "context_window": agent.context_window,
            "status": state.status if state else "unknown",
            "current_task": state.current_task if state else None,
            "progress": state.progress if state else 0.0,
            "stats": {
                "total_tasks": state.total_tasks if state else 0,
                "successful_tasks": state.successful_tasks if state else 0,
                "failed_tasks": state.failed_tasks if state else 0
            }
        }
    
    def create_agent_pipeline(
        self,
        task_description: str,
        pipeline_roles: List[AgentRole]
    ) -> Dict[str, Any]:
        """
        Create a pipeline of agents for complex tasks.
        Example: [ARCHITECT, DEVELOPER, TESTER, REVIEWER]
        """
        pipeline_id = f"pipeline-{uuid.uuid4().hex[:8]}"
        
        return {
            "pipeline_id": pipeline_id,
            "task_description": task_description,
            "stages": [
                {
                    "stage": i + 1,
                    "role": role.value,
                    "status": "pending",
                    "agent_id": None,
                    "result": None
                }
                for i, role in enumerate(pipeline_roles)
            ],
            "current_stage": 0,
            "created_at": time.time(),
            "status": "created"
        }
    
    async def execute_pipeline(
        self,
        pipeline: Dict[str, Any],
        initial_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an agent pipeline sequentially.
        Each agent receives the output of the previous agent.
        """
        context = initial_context.copy()
        
        for i, stage in enumerate(pipeline["stages"]):
            pipeline["current_stage"] = i
            stage["status"] = "running"
            
            # Find available agent for this role
            role = AgentRole(stage["role"])
            agent_id = await self.route_task(
                TaskContext(
                    task_id=f"{pipeline['pipeline_id']}-stage-{i}",
                    task_type=self._role_to_task_type(role),
                    description=pipeline["task_description"],
                    metadata=context
                ),
                preferred_agents=[role]
            )
            
            if not agent_id:
                stage["status"] = "failed"
                stage["error"] = "No available agent"
                pipeline["status"] = "failed"
                return pipeline
            
            stage["agent_id"] = agent_id
            
            # Here we would execute the agent with the context
            # For now, we'll just simulate
            # In production, this would call the agent execution engine
            
            stage["status"] = "completed"
            stage["completed_at"] = time.time()
        
        pipeline["status"] = "completed"
        pipeline["completed_at"] = time.time()
        
        return pipeline
    
    def _role_to_task_type(self, role: AgentRole) -> TaskType:
        """Convert agent role to task type"""
        mapping = {
            AgentRole.ARCHITECT: TaskType.ARCHITECTURE,
            AgentRole.DEVELOPER: TaskType.CODING,
            AgentRole.DEBUGGER: TaskType.DEBUGGING,
            AgentRole.TESTER: TaskType.TESTING,
            AgentRole.REVIEWER: TaskType.REVIEW,
            AgentRole.SECURITY_AUDITOR: TaskType.SECURITY,
            AgentRole.DOCUMENTATION: TaskType.DOCUMENTATION,
            AgentRole.DEVOPS: TaskType.DEVOPS,
        }
        return mapping.get(role, TaskType.CODING)
    
    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Get all currently active tasks"""
        return list(self.active_tasks.values())
    
    def get_task_history(
        self,
        limit: int = 100,
        agent_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get task history"""
        history = self.task_history[-limit:] if len(self.task_history) > limit else self.task_history
        
        if agent_id:
            history = [t for t in history if t.get("agent_id") == agent_id]
        
        return history
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get dashboard statistics"""
        total_agents = len(self.agents)
        idle_agents = sum(
            1 for s in self.agent_states.values() if s.status == "idle"
        )
        busy_agents = sum(
            1 for s in self.agent_states.values() if s.status == "busy"
        )
        error_agents = sum(
            1 for s in self.agent_states.values() if s.status == "error"
        )
        
        total_tasks = sum(s.total_tasks for s in self.agent_states.values())
        successful_tasks = sum(s.successful_tasks for s in self.agent_states.values())
        failed_tasks = sum(s.failed_tasks for s in self.agent_states.values())
        
        success_rate = (
            successful_tasks / total_tasks * 100 if total_tasks > 0 else 0.0
        )
        
        return {
            "total_agents": total_agents,
            "idle_agents": idle_agents,
            "busy_agents": busy_agents,
            "error_agents": error_agents,
            "active_tasks": len(self.active_tasks),
            "total_tasks_processed": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": round(success_rate, 2),
            "average_tasks_per_agent": round(
                total_tasks / total_agents, 2
            ) if total_agents > 0 else 0.0
        }


# Global instance
agent_router = AgentRouter()
