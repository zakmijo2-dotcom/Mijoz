"""File system tools for agent operations."""
from typing import Optional, List
import os
import aiofiles
from pathlib import Path


class FileSystemTools:
    """Tools for file system operations within a sandbox."""
    
    def __init__(self, sandbox):
        """
        Initialize with a sandbox instance.
        
        Args:
            sandbox: Sandbox instance that provides the isolated filesystem context
        """
        self.sandbox = sandbox
        self.base_path = sandbox.workspace_path
    
    async def read_file(self, path: str) -> str:
        """
        Read contents of a file.
        
        Args:
            path: Relative or absolute path to the file
            
        Returns:
            File contents as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If path is outside sandbox
        """
        # Resolve to absolute path within sandbox
        abs_path = await self._resolve_path(path)
        
        # Security check: ensure path is within sandbox
        if not str(abs_path).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {path} is outside sandbox")
        
        if not await aiofiles.os.path.exists(abs_path):
            raise FileNotFoundError(f"File not found: {path}")
        
        async with aiofiles.open(abs_path, 'r', encoding='utf-8') as f:
            return await f.read()
    
    async def write_file(self, path: str, content: str) -> None:
        """
        Write content to a file.
        
        Args:
            path: Relative or absolute path to the file
            content: Content to write
            
        Raises:
            PermissionError: If path is outside sandbox
        """
        abs_path = await self._resolve_path(path)
        
        # Security check
        if not str(abs_path).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {path} is outside sandbox")
        
        # Create parent directories if needed
        await aiofiles.os.makedirs(abs_path.parent, exist_ok=True)
        
        async with aiofiles.open(abs_path, 'w', encoding='utf-8') as f:
            await f.write(content)
    
    async def append_file(self, path: str, content: str) -> None:
        """Append content to a file."""
        abs_path = await self._resolve_path(path)
        
        if not str(abs_path).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {path} is outside sandbox")
        
        async with aiofiles.open(abs_path, 'a', encoding='utf-8') as f:
            await f.write(content)
    
    async def delete_file(self, path: str) -> None:
        """Delete a file."""
        abs_path = await self._resolve_path(path)
        
        if not str(abs_path).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {path} is outside sandbox")
        
        await aiofiles.os.remove(abs_path)
    
    async def list_directory(self, path: str = ".") -> List[str]:
        """List contents of a directory."""
        abs_path = await self._resolve_path(path)
        
        if not str(abs_path).startswith(str(self.base_path)):
            raise PermissionError(f"Access denied: {path} is outside sandbox")
        
        if not await aiofiles.os.path.isdir(abs_path):
            raise NotADirectoryError(f"Not a directory: {path}")
        
        return os.listdir(abs_path)
    
    async def file_exists(self, path: str) -> bool:
        """Check if a file exists."""
        try:
            abs_path = await self._resolve_path(path)
            return await aiofiles.os.path.isfile(abs_path)
        except:
            return False
    
    async def _resolve_path(self, path: str) -> Path:
        """Resolve a path to absolute path within sandbox."""
        p = Path(path)
        
        if p.is_absolute():
            return p
        else:
            return self.base_path / p
