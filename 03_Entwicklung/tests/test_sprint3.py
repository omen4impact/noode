"""Tests for Sprint 3 components."""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime

from noode.core.session_manager import SessionManager, AgentSession


class TestSessionManager:
    """Tests for SessionManager."""
    
    def test_init_memory(self) -> None:
        """Test in-memory session manager."""
        manager = SessionManager()
        assert manager.storage_path is None
        assert len(manager._sessions) == 0
    
    def test_create_session(self) -> None:
        """Test session creation."""
        manager = SessionManager()
        session = manager.create_session(
            agent_name="test_agent",
            project_id="proj123",
        )
        
        assert session.session_id is not None
        assert session.agent_name == "test_agent"
        assert session.project_id == "proj123"
        assert session.is_active is True
    
    def test_get_session(self) -> None:
        """Test session retrieval."""
        manager = SessionManager()
        created = manager.create_session("agent1")
        
        retrieved = manager.get_session(created.session_id)
        assert retrieved is not None
        assert retrieved.session_id == created.session_id
    
    def test_update_session_context(self) -> None:
        """Test updating session context."""
        manager = SessionManager()
        session = manager.create_session("agent1")
        
        updated = manager.update_session(
            session.session_id,
            context={"key": "value"},
        )
        
        assert updated is not None
        assert updated.context["key"] == "value"
    
    def test_update_session_message(self) -> None:
        """Test adding messages to session."""
        manager = SessionManager()
        session = manager.create_session("agent1")
        
        updated = manager.update_session(
            session.session_id,
            message={"role": "user", "content": "Hello"},
        )
        
        assert updated is not None
        assert len(updated.messages) == 1
        assert updated.messages[0]["content"] == "Hello"
    
    def test_close_session(self) -> None:
        """Test closing a session."""
        manager = SessionManager()
        session = manager.create_session("agent1")
        
        result = manager.close_session(session.session_id)
        assert result is True
        
        closed = manager.get_session(session.session_id)
        assert closed is not None
        assert closed.is_active is False
    
    def test_list_sessions(self) -> None:
        """Test listing sessions."""
        manager = SessionManager()
        manager.create_session("agent1")
        manager.create_session("agent1")
        manager.create_session("agent2")
        
        # All active
        all_sessions = manager.list_sessions()
        assert len(all_sessions) == 3
        
        # Filter by agent
        agent1_sessions = manager.list_sessions(agent_name="agent1")
        assert len(agent1_sessions) == 2
    
    def test_get_stats(self) -> None:
        """Test statistics."""
        manager = SessionManager()
        session = manager.create_session("agent1")
        manager.update_session(session.session_id, task_completed=True)
        manager.update_session(session.session_id, task_completed=True)
        
        stats = manager.get_stats()
        assert stats["total_sessions"] == 1
        assert stats["active_sessions"] == 1
        assert stats["total_tasks_completed"] == 2
    
    def test_persistence(self) -> None:
        """Test session persistence."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "sessions"
            
            # Create session
            manager1 = SessionManager(storage_path=storage_path)
            session = manager1.create_session(
                agent_name="test_agent",
                context={"test": "data"},
            )
            session_id = session.session_id
            
            # Load in new manager
            manager2 = SessionManager(storage_path=storage_path)
            loaded = manager2.get_session(session_id)
            
            assert loaded is not None
            assert loaded.agent_name == "test_agent"
            assert loaded.context["test"] == "data"


class TestAgentSession:
    """Tests for AgentSession dataclass."""
    
    def test_to_dict(self) -> None:
        """Test serialization."""
        session = AgentSession(
            session_id="abc123",
            agent_name="test",
            created_at=datetime(2026, 1, 1),
            last_active=datetime(2026, 1, 2),
            context={"key": "val"},
        )
        
        data = session.to_dict()
        assert data["session_id"] == "abc123"
        assert data["agent_name"] == "test"
        assert "created_at" in data
    
    def test_from_dict(self) -> None:
        """Test deserialization."""
        data = {
            "session_id": "xyz",
            "agent_name": "agent",
            "created_at": "2026-01-01T00:00:00",
            "last_active": "2026-01-02T00:00:00",
            "context": {},
            "messages": [],
        }
        
        session = AgentSession.from_dict(data)
        assert session.session_id == "xyz"
        assert session.agent_name == "agent"
