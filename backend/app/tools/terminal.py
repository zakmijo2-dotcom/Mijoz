"""Terminal tools for executing shell commands in sandbox."""
from typing import Optional, Dict, Any
import asyncio
import subprocess


class TerminalTools:
    """Tools for executing terminal commands within a sandbox."""
    
    def __init__(self, sandbox):
        """
        Initialize with a sandbox instance.
        
        Args:
            sandbox: Sandbox instance that provides execution context
        """
        self.sandbox = sandbox
        self.base_path = sandbox.workspace_path
        self.allowed_commands = sandbox.allowed_commands or []
    
    async def run_command(
        self, 
        command: str, 
        timeout: int = 60,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        Execute a shell command in the sandbox.
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds
            cwd: Working directory (relative to sandbox)
            env: Environment variables
            
        Returns:
            Dict with stdout, stderr, return_code
            
        Raises:
            PermissionError: If command is not allowed
            TimeoutError: If command exceeds timeout
        """
        # Security check: validate command is allowed
        if not self._is_command_allowed(command):
            raise PermissionError(
                f"Command not allowed: {command}. "
                f"Allowed commands: {self.allowed_commands}"
            )
        
        # Set working directory
        work_dir = self.base_path / cwd if cwd else self.base_path
        
        # Ensure working directory is within sandbox
        if not str(work_dir).startswith(str(self.base_path)):
            raise PermissionError(f"Working directory outside sandbox: {cwd}")
        
        # Merge environment
        full_env = self.sandbox.get_environment()
        if env:
            full_env.update(env)
        
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                env=full_env,
                limit=10 * 1024 * 1024,  # 10MB buffer
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
                
                return {
                    "stdout": stdout.decode('utf-8', errors='replace'),
                    "stderr": stderr.decode('utf-8', errors='replace'),
                    "return_code": process.returncode,
                    "pid": process.pid,
                }
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise TimeoutError(f"Command timed out after {timeout}s: {command}")
                
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "error": True
            }
    
    def _is_command_allowed(self, command: str) -> bool:
        """Check if command is in the allowed list."""
        if not self.allowed_commands:
            return False
        
        # Extract base command
        base_cmd = command.split()[0] if command.split() else ""
        
        # Check against allowed patterns
        for allowed in self.allowed_commands:
            if allowed == "*":
                return True
            if allowed.endswith("/*"):
                # Pattern match (e.g., "npm/*" matches "npm install", "npm test")
                prefix = allowed[:-1]  # "npm/"
                if command.startswith(prefix):
                    return True
            if base_cmd == allowed:
                return True
        
        return False
    
    async def run_script(self, script: str, interpreter: str = "bash") -> Dict[str, Any]:
        """Run a script string through an interpreter."""
        if interpreter not in self.allowed_commands:
            raise PermissionError(f"Interpreter not allowed: {interpreter}")
        
        return await self.run_command(f"{interpreter} -c '{script}'")
