"""
Docker Sandbox Manager - Secure isolated execution environments for AI agents
"""

import asyncio
import os
import uuid
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import docker
from docker.models.containers import Container
from docker.errors import DockerException, NotFound

from ..models.router_models import AgentRole


class SandboxConfig:
    """Configuration for sandbox creation"""
    
    def __init__(
        self,
        project_id: str,
        agent_role: AgentRole,
        cpu_limit: float = 2.0,
        memory_limit: str = "2g",
        disk_limit: str = "10g",
        network_enabled: bool = False,
        timeout_seconds: int = 300,
        allowed_commands: Optional[List[str]] = None,
        read_only_filesystem: bool = True,
        workspace_path: str = "/workspace"
    ):
        self.project_id = project_id
        self.agent_role = agent_role
        self.cpu_limit = cpu_limit
        self.memory_limit = memory_limit
        self.disk_limit = disk_limit
        self.network_enabled = network_enabled
        self.timeout_seconds = timeout_seconds
        self.allowed_commands = allowed_commands or []
        self.read_only_filesystem = read_only_filesystem
        self.workspace_path = workspace_path


class SandboxSession:
    """Represents an active sandbox session"""
    
    def __init__(
        self,
        session_id: str,
        container: Container,
        config: SandboxConfig,
        created_at: datetime
    ):
        self.session_id = session_id
        self.container = container
        self.config = config
        self.created_at = created_at
        self.last_activity = created_at
        self.exec_history: List[Dict[str, Any]] = []
        self.file_changes: List[str] = []
        self.is_active = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "container_id": self.container.id[:12],
            "project_id": self.config.project_id,
            "agent_role": self.config.agent_role.value,
            "status": "active" if self.is_active else "stopped",
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "exec_count": len(self.exec_history),
            "file_changes_count": len(self.file_changes)
        }


class DockerSandboxManager:
    """
    Manages secure Docker sandboxes for AI agent code execution.
    Provides isolation, resource limits, and audit logging.
    """
    
    def __init__(self, docker_client: Optional[docker.DockerClient] = None):
        try:
            self.client = docker_client or docker.from_env()
            # Test connection
            self.client.ping()
            self.docker_available = True
        except Exception:
            self.client = None
            self.docker_available = False
        
        self.sessions: Dict[str, SandboxSession] = {}
        self.project_sandboxes: Dict[str, List[str]] = {}  # project_id -> [session_ids]
        self._lock = asyncio.Lock()
        
        # Default security settings
        self.default_capabilities_drop = ["ALL"]
        self.default_capabilities_add = ["CHOWN", "SETUID", "SETGID"]
        self.default_security_opts = ["no-new-privileges:true"]
        
        # Allowed commands per agent role
        self.role_allowed_commands = {
            AgentRole.ARCHITECT: ["cat", "ls", "find", "grep", "head", "tail"],
            AgentRole.DEVELOPER: [
                "cat", "ls", "find", "grep", "head", "tail",
                "npm", "npx", "node", "python", "pip", "git",
                "mkdir", "touch", "cp", "mv", "rm"
            ],
            AgentRole.DEBUGGER: [
                "cat", "ls", "find", "grep", "head", "tail",
                "npm", "npx", "node", "python", "pip",
                "pytest", "jest", "mocha"
            ],
            AgentRole.TESTER: [
                "cat", "ls", "find", "grep", "head", "tail",
                "npm", "npx", "node", "python", "pip",
                "pytest", "jest", "mocha", "coverage"
            ],
            AgentRole.REVIEWER: ["cat", "ls", "find", "grep", "head", "tail", "git"],
            AgentRole.SECURITY_AUDITOR: [
                "cat", "ls", "find", "grep", "head", "tail",
                "npm", "npx", "node", "python", "pip",
                "audit", "snyk", "trivy"
            ],
            AgentRole.DOCUMENTATION: [
                "cat", "ls", "find", "grep", "head", "tail",
                "mkdir", "touch", "cp", "mv"
            ],
            AgentRole.DEVOPS: [
                "cat", "ls", "find", "grep", "head", "tail",
                "npm", "npx", "node", "python", "pip",
                "docker", "kubectl", "terraform", "ansible",
                "mkdir", "touch", "cp", "mv", "rm", "chmod"
            ]
        }
    
    async def create_sandbox(
        self,
        config: SandboxConfig,
        image: str = "mijoz-sandbox:latest",
        environment: Optional[Dict[str, str]] = None
    ) -> SandboxSession:
        """
        Create a new isolated sandbox for an agent.
        """
        async with self._lock:
            session_id = f"sandbox-{uuid.uuid4().hex[:12]}"
            
            # Get allowed commands for the agent role
            allowed_commands = config.allowed_commands or \
                             self.role_allowed_commands.get(config.agent_role, [])
            
            # Build container configuration
            container_config = {
                "image": image,
                "name": f"mijoz-{session_id}",
                "detach": True,
                "tty": True,
                "stdin_open": True,
                "working_dir": config.workspace_path,
                "environment": environment or {},
                
                # Resource limits
                "nano_cpus": int(config.cpu_limit * 1e9),
                "mem_limit": config.memory_limit,
                
                # Security settings
                "cap_drop": self.default_capabilities_drop,
                "cap_add": self.default_capabilities_add,
                "security_opt": self.default_security_opts,
                
                # Filesystem
                "read_only": config.read_only_filesystem,
                
                # Network isolation
                "network_disabled": not config.network_enabled,
                
                # Labels for management
                "labels": {
                    "mijoz.session_id": session_id,
                    "mijoz.project_id": config.project_id,
                    "mijoz.agent_role": config.agent_role.value,
                    "mijoz.created_at": datetime.now().isoformat()
                }
            }
            
            # Create tmpfs for writable directories if read-only filesystem
            if config.read_only_filesystem:
                container_config["tmpfs"] = {
                    "/tmp": "rw,noexec,nosuid,size=512m",
                    config.workspace_path: f"rw,noexec,nosuid,size={config.disk_limit}"
                }
            
            # Create volumes for project persistence
            volumes = {
                f"mijoz-project-{config.project_id}": {
                    "bind": config.workspace_path,
                    "mode": "rw"
                }
            }
            container_config["volumes"] = volumes
            
            try:
                # Create and start container
                container = self.client.containers.run(**container_config)
                
                session = SandboxSession(
                    session_id=session_id,
                    container=container,
                    config=config,
                    created_at=datetime.now()
                )
                
                self.sessions[session_id] = session
                
                # Track by project
                if config.project_id not in self.project_sandboxes:
                    self.project_sandboxes[config.project_id] = []
                self.project_sandboxes[config.project_id].append(session_id)
                
                return session
                
            except DockerException as e:
                raise RuntimeError(f"Failed to create sandbox: {str(e)}")
    
    async def execute_command(
        self,
        session_id: str,
        command: str,
        user: str = "sandbox",
        workdir: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute a command inside a sandbox.
        Returns execution result with stdout, stderr, exit_code.
        """
        async with self._lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            if not session.is_active:
                raise ValueError(f"Session {session_id} is not active")
            
            # Validate command against allowed list
            base_command = command.split()[0] if command else ""
            allowed = session.config.allowed_commands or \
                     self.role_allowed_commands.get(session.config.agent_role, [])
            
            if allowed and base_command not in allowed:
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": f"Command '{base_command}' is not allowed",
                    "blocked": True
                }
            
            try:
                # Execute command
                exec_result = session.container.exec_run(
                    cmd=command,
                    user=user,
                    workdir=workdir,
                    environment=environment,
                    tty=False,
                    stream=False,
                    demux=True
                )
                
                exit_code = exec_result.exit_code
                output = exec_result.output
                
                # Demux stdout/stderr
                stdout = output[0].decode() if output[0] else ""
                stderr = output[1].decode() if output[1] else ""
                
                # Record execution
                session.exec_history.append({
                    "timestamp": datetime.now().isoformat(),
                    "command": command,
                    "exit_code": exit_code,
                    "user": user
                })
                
                # Update last activity
                session.last_activity = datetime.now()
                
                return {
                    "success": exit_code == 0,
                    "exit_code": exit_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "blocked": False
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "blocked": False
                }
    
    async def read_file(
        self,
        session_id: str,
        file_path: str,
        max_size: int = 1_000_000  # 1MB limit
    ) -> Dict[str, Any]:
        """Read a file from the sandbox"""
        async with self._lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            try:
                # Use cat command with size limit
                result = await self.execute_command(
                    session_id,
                    f"head -c {max_size} \"{file_path}\""
                )
                
                if result["success"]:
                    return {
                        "success": True,
                        "content": result["stdout"],
                        "truncated": len(result["stdout"]) >= max_size
                    }
                else:
                    return {
                        "success": False,
                        "error": result["stderr"]
                    }
                    
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def write_file(
        self,
        session_id: str,
        file_path: str,
        content: str
    ) -> Dict[str, Any]:
        """Write a file to the sandbox"""
        async with self._lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            # Check if write is allowed
            if "write_files" not in session.config.permissions or \
               not session.config.permissions["write_files"]:
                return {
                    "success": False,
                    "error": "Write permission not granted"
                }
            
            try:
                # Escape content for shell
                escaped_content = content.replace("'", "'\"'\"'")
                
                # Create directory if needed
                dir_path = "/".join(file_path.split("/")[:-1])
                if dir_path:
                    await self.execute_command(session_id, f"mkdir -p {dir_path}")
                
                # Write file using heredoc
                result = await self.execute_command(
                    session_id,
                    f"cat > '{file_path}' << 'EOF'\n{content}\nEOF"
                )
                
                if result["success"]:
                    session.file_changes.append(file_path)
                    return {"success": True}
                else:
                    return {"success": False, "error": result["stderr"]}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def get_file_list(
        self,
        session_id: str,
        path: str = "/workspace"
    ) -> Dict[str, Any]:
        """Get list of files in a directory"""
        async with self._lock:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            
            try:
                result = await self.execute_command(
                    session_id,
                    f"find {path} -type f -o -type d | head -1000"
                )
                
                if result["success"]:
                    files = result["stdout"].strip().split("\n")
                    return {
                        "success": True,
                        "files": files,
                        "count": len(files)
                    }
                else:
                    return {"success": False, "error": result["stderr"]}
                    
            except Exception as e:
                return {"success": False, "error": str(e)}
    
    async def stop_sandbox(self, session_id: str, timeout: int = 10) -> bool:
        """Stop and remove a sandbox"""
        async with self._lock:
            if session_id not in self.sessions:
                return False
            
            session = self.sessions[session_id]
            
            try:
                session.container.stop(timeout=timeout)
                session.container.remove(force=True)
                session.is_active = False
                
                # Remove from tracking
                del self.sessions[session_id]
                
                # Remove from project tracking
                project_id = session.config.project_id
                if project_id in self.project_sandboxes:
                    if session_id in self.project_sandboxes[project_id]:
                        self.project_sandboxes[project_id].remove(session_id)
                
                return True
                
            except Exception as e:
                print(f"Error stopping sandbox {session_id}: {e}")
                return False
    
    async def stop_all_project_sandboxes(
        self,
        project_id: str,
        timeout: int = 10
    ) -> int:
        """Stop all sandboxes for a project"""
        count = 0
        
        if project_id in self.project_sandboxes:
            session_ids = self.project_sandboxes[project_id].copy()
            for session_id in session_ids:
                if await self.stop_sandbox(session_id, timeout):
                    count += 1
        
        return count
    
    async def cleanup_stale_sandboxes(
        self,
        max_age_seconds: int = 3600
    ) -> int:
        """Remove sandboxes that have been inactive too long"""
        count = 0
        now = datetime.now()
        
        async with self._lock:
            stale_sessions = []
            
            for session_id, session in self.sessions.items():
                age = (now - session.last_activity).total_seconds()
                if age > max_age_seconds:
                    stale_sessions.append(session_id)
            
            for session_id in stale_sessions:
                if await self.stop_sandbox(session_id):
                    count += 1
        
        return count
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        return self.sessions[session_id].to_dict()
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        return [session.to_dict() for session in self.sessions.values()]
    
    def get_project_sessions(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all sessions for a project"""
        if project_id not in self.project_sandboxes:
            return []
        
        sessions = []
        for session_id in self.project_sandboxes[project_id]:
            if session_id in self.sessions:
                sessions.append(self.sessions[session_id].to_dict())
        
        return sessions
    
    def get_execution_history(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get command execution history for a session"""
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id].exec_history
        return history[-limit:]
    
    def get_audit_log(
        self,
        project_id: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Get audit log of all executions"""
        logs = []
        
        for session in self.sessions.values():
            if project_id and session.config.project_id != project_id:
                continue
            
            for exec_entry in session.exec_history:
                logs.append({
                    "session_id": session.session_id,
                    "project_id": session.config.project_id,
                    "agent_role": session.config.agent_role.value,
                    "timestamp": exec_entry["timestamp"],
                    "command": exec_entry["command"],
                    "exit_code": exec_entry["exit_code"]
                })
        
        # Sort by timestamp
        logs.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return logs[:limit]


# Global instance
sandbox_manager = DockerSandboxManager()
