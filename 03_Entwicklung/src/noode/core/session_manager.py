"""Persistent session management for agents.

Manages agent sessions with state persistence across restarts.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger()


@dataclass
class AgentSession:
    """An agent session with state."""
    
    session_id: str
    agent_name: str
    created_at: datetime
    last_active: datetime
    project_id: str | None = None
    context: dict[str, Any] = field(default_factory=dict)
    messages: list[dict[str, str]] = field(default_factory=list)
    tasks_completed: int = 0
    is_active: bool = True
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize session to dict."""
        return {
            "session_id": self.session_id,
            "agent_name": self.agent_name,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "project_id": self.project_id,
            "context": self.context,
            "messages": self.messages,
            "tasks_completed": self.tasks_completed,
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentSession":
        """Deserialize session from dict."""
        return cls(
            session_id=data["session_id"],
            agent_name=data["agent_name"],
            created_at=datetime.fromisoformat(data["created_at"]),
            last_active=datetime.fromisoformat(data["last_active"]),
            project_id=data.get("project_id"),
            context=data.get("context", {}),
            messages=data.get("messages", []),
            tasks_completed=data.get("tasks_completed", 0),
            is_active=data.get("is_active", True),
        )


class SessionManager:
    """Manage persistent agent sessions."""
    
    def __init__(
        self,
        storage_path: Path | None = None,
        max_sessions_per_agent: int = 10,
    ) -> None:
        """Initialize session manager.
        
        Args:
            storage_path: Path for session persistence
            max_sessions_per_agent: Maximum active sessions per agent
        """
        self.storage_path = storage_path
        self.max_sessions = max_sessions_per_agent
        self._sessions: dict[str, AgentSession] = {}
        
        if storage_path:
            storage_path.mkdir(parents=True, exist_ok=True)
            self._load_sessions()
    
    def create_session(
        self,
        agent_name: str,
        project_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> AgentSession:
        """Create a new session.
        
        Args:
            agent_name: Name of the agent
            project_id: Optional project context
            context: Initial context
            
        Returns:
            Created session
        """
        session_id = str(uuid4())[:12]
        now = datetime.now()
        
        session = AgentSession(
            session_id=session_id,
            agent_name=agent_name,
            created_at=now,
            last_active=now,
            project_id=project_id,
            context=context or {},
        )
        
        self._sessions[session_id] = session
        
        # Enforce session limit per agent
        self._cleanup_old_sessions(agent_name)
        
        # Persist
        self._save_session(session)
        
        logger.info(
            "session_created",
            session_id=session_id,
            agent=agent_name,
        )
        
        return session
    
    def get_session(self, session_id: str) -> AgentSession | None:
        """Get a session by ID.
        
        Args:
            session_id: Session ID
            
        Returns:
            Session or None
        """
        return self._sessions.get(session_id)
    
    def update_session(
        self,
        session_id: str,
        context: dict[str, Any] | None = None,
        message: dict[str, str] | None = None,
        task_completed: bool = False,
    ) -> AgentSession | None:
        """Update a session.
        
        Args:
            session_id: Session ID
            context: Context updates to merge
            message: Message to add
            task_completed: Whether a task was completed
            
        Returns:
            Updated session or None
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        session.last_active = datetime.now()
        
        if context:
            session.context.update(context)
        
        if message:
            session.messages.append(message)
            # Keep last 100 messages
            if len(session.messages) > 100:
                session.messages = session.messages[-100:]
        
        if task_completed:
            session.tasks_completed += 1
        
        self._save_session(session)
        
        return session
    
    def close_session(self, session_id: str) -> bool:
        """Close a session.
        
        Args:
            session_id: Session ID
            
        Returns:
            True if closed
        """
        session = self._sessions.get(session_id)
        if not session:
            return False
        
        session.is_active = False
        session.last_active = datetime.now()
        self._save_session(session)
        
        logger.info("session_closed", session_id=session_id)
        
        return True
    
    def list_sessions(
        self,
        agent_name: str | None = None,
        active_only: bool = True,
    ) -> list[AgentSession]:
        """List sessions.
        
        Args:
            agent_name: Filter by agent
            active_only: Only show active sessions
            
        Returns:
            List of sessions
        """
        sessions = list(self._sessions.values())
        
        if agent_name:
            sessions = [s for s in sessions if s.agent_name == agent_name]
        
        if active_only:
            sessions = [s for s in sessions if s.is_active]
        
        return sorted(sessions, key=lambda s: s.last_active, reverse=True)
    
    def get_agent_context(self, agent_name: str) -> dict[str, Any]:
        """Get combined context from all active sessions for an agent.
        
        Args:
            agent_name: Agent name
            
        Returns:
            Combined context
        """
        sessions = self.list_sessions(agent_name=agent_name, active_only=True)
        
        context: dict[str, Any] = {}
        for session in sessions:
            context.update(session.context)
        
        return context
    
    def _cleanup_old_sessions(self, agent_name: str) -> None:
        """Clean up old sessions for an agent."""
        sessions = self.list_sessions(agent_name=agent_name, active_only=True)
        
        while len(sessions) > self.max_sessions:
            oldest = sessions.pop()
            oldest.is_active = False
            self._save_session(oldest)
    
    def _save_session(self, session: AgentSession) -> None:
        """Persist session to disk."""
        if not self.storage_path:
            return
        
        session_file = self.storage_path / f"{session.session_id}.json"
        session_file.write_text(json.dumps(session.to_dict(), indent=2))
    
    def _load_sessions(self) -> None:
        """Load sessions from disk."""
        if not self.storage_path:
            return
        
        for session_file in self.storage_path.glob("*.json"):
            try:
                data = json.loads(session_file.read_text())
                session = AgentSession.from_dict(data)
                self._sessions[session.session_id] = session
            except Exception as e:
                logger.warning(
                    "session_load_failed",
                    file=str(session_file),
                    error=str(e),
                )
        
        logger.info("sessions_loaded", count=len(self._sessions))
    
    def get_stats(self) -> dict[str, Any]:
        """Get session statistics.
        
        Returns:
            Statistics dict
        """
        active = [s for s in self._sessions.values() if s.is_active]
        
        by_agent: dict[str, int] = {}
        for session in active:
            by_agent[session.agent_name] = by_agent.get(session.agent_name, 0) + 1
        
        return {
            "total_sessions": len(self._sessions),
            "active_sessions": len(active),
            "by_agent": by_agent,
            "total_tasks_completed": sum(s.tasks_completed for s in active),
        }
