"""Events module for agent execution events and WebSocket handling."""
from typing import Dict, List, Callable, Any
import asyncio
import json
from datetime import datetime


class EventBroker:
    """Central event broker for agent execution events."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: Dict[str, List[dict]] = {}
        self.max_history_per_session = 100
    
    def subscribe(self, session_id: str, callback: Callable) -> None:
        """Subscribe to events for a specific session."""
        if session_id not in self.subscribers:
            self.subscribers[session_id] = []
        self.subscribers[session_id].append(callback)
    
    def unsubscribe(self, session_id: str, callback: Callable) -> None:
        """Unsubscribe from events for a specific session."""
        if session_id in self.subscribers:
            self.subscribers[session_id].remove(callback)
    
    async def publish(self, session_id: str, event_type: str, data: dict) -> None:
        """Publish an event to all subscribers of a session."""
        event = {
            "event_type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "session_id": session_id,
        }
        
        # Store in history
        if session_id not in self.event_history:
            self.event_history[session_id] = []
        self.event_history[session_id].append(event)
        
        # Trim history if needed
        if len(self.event_history[session_id]) > self.max_history_per_session:
            self.event_history[session_id] = self.event_history[session_id][-self.max_history_per_session:]
        
        # Notify subscribers
        if session_id in self.subscribers:
            for callback in self.subscribers[session_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(event)
                    else:
                        callback(event)
                except Exception as e:
                    print(f"Error notifying subscriber: {e}")
    
    def get_history(self, session_id: str, limit: int = 50) -> List[dict]:
        """Get recent event history for a session."""
        if session_id not in self.event_history:
            return []
        return self.event_history[session_id][-limit:]
    
    def clear_history(self, session_id: str) -> None:
        """Clear event history for a session."""
        if session_id in self.event_history:
            del self.event_history[session_id]


# Global event broker instance
event_broker = EventBroker()
