"""Agent Executor - Core runtime for executing AI agents with tools and sandbox."""
from typing import Optional, Dict, Any, List, AsyncGenerator
from datetime import datetime
import json
import asyncio
from enum import Enum

from app.services.agent_router import AgentRegistry, AgentDefinition
from app.services.model_router import ModelRouter
from app.sandbox.manager import SandboxManager
from app.tools.filesystem import FileSystemTools
from app.tools.terminal import TerminalTools


class AgentStatus(str, Enum):
    """Agent execution status."""
    PENDING = "pending"
    THINKING = "thinking"
    EXECUTING_TOOL = "executing_tool"
    WAITING_FOR_MODEL = "waiting_for_model"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ToolCallResult:
    """Result of a tool execution."""
    def __init__(self, tool_name: str, success: bool, result: Any, error: Optional[str] = None):
        self.tool_name = tool_name
        self.success = success
        self.result = result
        self.error = error
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result,
            "error": self.error,
            "timestamp": self.timestamp.isoformat()
        }


class AgentEvent:
    """Event emitted during agent execution."""
    def __init__(self, event_type: str, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.utcnow()
    
    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat()
        }


class AgentExecutor:
    """
    Executes AI agents in a loop: Think → Choose Tool → Execute → Observe → Repeat
    
    This is the core runtime that makes agents actually work, not just simulate.
    """
    
    def __init__(
        self,
        agent_registry: AgentRegistry,
        model_router: ModelRouter,
        sandbox_manager: SandboxManager,
    ):
        self.agent_registry = agent_registry
        self.model_router = model_router
        self.sandbox_manager = sandbox_manager
        
        # Tool instances per agent
        self.fs_tools: Dict[str, FileSystemTools] = {}
        self.terminal_tools: Dict[str, TerminalTools] = {}
        
        # Event subscribers
        self.event_subscribers: Dict[str, List[callable]] = {}
    
    async def execute_agent(
        self,
        agent_type: str,
        task: str,
        project_id: int,
        user_id: int,
        session_id: Optional[int] = None,
        max_iterations: int = 50,
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Execute an agent with the given task.
        
        Yields events throughout the execution lifecycle.
        """
        # Get agent definition
        agent_def = self.agent_registry.get_agent(agent_type)
        if not agent_def:
            yield AgentEvent("error", {"message": f"Agent {agent_type} not found"})
            return
        
        # Create or get sandbox for this project/user
        sandbox_id = f"project-{project_id}-user-{user_id}"
        try:
            sandbox = await self.sandbox_manager.get_or_create_sandbox(
                sandbox_id=sandbox_id,
                user_id=user_id,
                project_id=project_id,
            )
        except Exception as e:
            yield AgentEvent("error", {"message": f"Failed to create sandbox: {str(e)}"})
            return
        
        # Initialize tools for this sandbox
        fs_tools = FileSystemTools(sandbox)
        terminal_tools = TerminalTools(sandbox)
        
        # Build initial context
        messages = [
            {"role": "system", "content": agent_def.system_prompt},
            {"role": "user", "content": task}
        ]
        
        iteration = 0
        status = AgentStatus.THINKING
        
        while iteration < max_iterations:
            iteration += 1
            
            # Emit thinking event
            yield AgentEvent("status", {
                "status": AgentStatus.THINKING.value,
                "iteration": iteration,
                "message": f"Agent {agent_type} is thinking..."
            })
            
            # Select best model for this agent/task
            model_choice = await self.model_router.select_model(
                agent_type=agent_type,
                task_complexity="medium",  # Could analyze task to determine complexity
                urgency="normal",
                budget_sensitivity=agent_def.budget_limit is not None,
            )
            
            # Call LLM
            yield AgentEvent("model_call", {
                "model": model_choice.model_name,
                "provider": model_choice.provider,
                "messages_count": len(messages),
            })
            
            try:
                # Get response from model
                response = await self._call_llm(
                    model_name=model_choice.model_name,
                    provider=model_choice.provider,
                    messages=messages,
                    tools=self._get_tools_schema(agent_def),
                )
                
                # Parse response
                if response.get("tool_calls"):
                    # Agent wants to call tools
                    status = AgentStatus.EXECUTING_TOOL
                    
                    for tool_call in response["tool_calls"]:
                        yield AgentEvent("tool_call_start", {
                            "tool_name": tool_call["name"],
                            "arguments": tool_call["arguments"],
                        })
                        
                        # Execute tool
                        result = await self._execute_tool(
                            tool_name=tool_call["name"],
                            arguments=tool_call["arguments"],
                            fs_tools=fs_tools,
                            terminal_tools=terminal_tools,
                            agent_def=agent_def,
                        )
                        
                        yield AgentEvent("tool_call_end", result.to_dict())
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [tool_call]
                        })
                        messages.append({
                            "role": "tool",
                            "name": tool_call["name"],
                            "content": json.dumps(result.result) if result.success else result.error,
                            "tool_call_id": tool_call.get("id")
                        })
                        
                        if not result.success:
                            # Tool failed - agent may retry or fail
                            pass
                    
                    # Continue loop - agent will think again with tool results
                    continue
                else:
                    # Agent has final answer
                    status = AgentStatus.COMPLETED
                    yield AgentEvent("completed", {
                        "response": response.get("content"),
                        "iterations": iteration,
                        "tool_calls_count": sum(1 for m in messages if m.get("role") == "tool"),
                    })
                    return
                    
            except Exception as e:
                status = AgentStatus.FAILED
                yield AgentEvent("error", {
                    "message": str(e),
                    "iteration": iteration,
                })
                return
        
        # Max iterations reached
        status = AgentStatus.FAILED
        yield AgentEvent("error", {
            "message": f"Max iterations ({max_iterations}) reached",
            "iterations": iteration,
        })
    
    async def _call_llm(
        self,
        model_name: str,
        provider: str,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Call the LLM through the model router."""
        # Use model router's proxy to make the actual API call
        response = await self.model_router.proxy.send_request(
            model_name=model_name,
            messages=messages,
            tools=tools,
            temperature=0.7,
            max_tokens=4096,
        )
        
        # Parse response based on provider format
        # This would be handled by the proxy layer's response translation
        return response
    
    def _get_tools_schema(self, agent_def: AgentDefinition) -> List[Dict]:
        """Get OpenAI-style tools schema for allowed tools."""
        tools_schema = []
        
        if "read_file" in agent_def.allowed_tools:
            tools_schema.append({
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"}
                        },
                        "required": ["path"]
                    }
                }
            })
        
        if "write_file" in agent_def.allowed_tools:
            tools_schema.append({
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "Write content to a file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string", "description": "Path to the file"},
                            "content": {"type": "string", "description": "Content to write"}
                        },
                        "required": ["path", "content"]
                    }
                }
            })
        
        if "run_command" in agent_def.allowed_tools:
            tools_schema.append({
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Execute a shell command",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {"type": "string", "description": "Command to execute"},
                            "timeout": {"type": "integer", "description": "Timeout in seconds"}
                        },
                        "required": ["command"]
                    }
                }
            })
        
        return tools_schema
    
    async def _execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        fs_tools: FileSystemTools,
        terminal_tools: TerminalTools,
        agent_def: AgentDefinition,
    ) -> ToolCallResult:
        """Execute a tool call with permission checking."""
        # Check if tool is allowed for this agent
        if tool_name not in agent_def.allowed_tools:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=f"Tool {tool_name} not allowed for agent {agent_def.name}"
            )
        
        try:
            if tool_name == "read_file":
                content = await fs_tools.read_file(arguments["path"])
                return ToolCallResult(tool_name, True, content)
            
            elif tool_name == "write_file":
                await fs_tools.write_file(arguments["path"], arguments["content"])
                return ToolCallResult(tool_name, True, {"status": "success"})
            
            elif tool_name == "run_command":
                output = await terminal_tools.run_command(
                    arguments["command"],
                    timeout=arguments.get("timeout", 60)
                )
                return ToolCallResult(tool_name, True, output)
            
            else:
                return ToolCallResult(
                    tool_name=tool_name,
                    success=False,
                    result=None,
                    error=f"Unknown tool: {tool_name}"
                )
                
        except Exception as e:
            return ToolCallResult(
                tool_name=tool_name,
                success=False,
                result=None,
                error=str(e)
            )
    
    def subscribe_events(self, session_id: str, callback: callable):
        """Subscribe to agent events for a session."""
        if session_id not in self.event_subscribers:
            self.event_subscribers[session_id] = []
        self.event_subscribers[session_id].append(callback)
    
    def unsubscribe_events(self, session_id: str, callback: callable):
        """Unsubscribe from agent events."""
        if session_id in self.event_subscribers:
            self.event_subscribers[session_id].remove(callback)
