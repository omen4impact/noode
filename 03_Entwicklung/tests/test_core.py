"""Tests for core agent functionality."""

import pytest
from datetime import datetime

from noode.core.memory import AgentMemory, MemoryEntry
from noode.protocols.messages import AgentMessage, MessageType, Priority
from noode.protocols.consensus import ConsensusBuilder, Vote, VoteType


class TestAgentMemory:
    """Tests for AgentMemory class."""
    
    def test_init(self) -> None:
        """Test memory initialization."""
        memory = AgentMemory(agent_name="test_agent")
        assert memory.agent_name == "test_agent"
        assert memory.max_short_term == 100
    
    def test_add_message(self) -> None:
        """Test adding conversation messages."""
        memory = AgentMemory(agent_name="test")
        memory.add_message("user", "Hello")
        memory.add_message("assistant", "Hi there")
        
        messages = memory.get_recent_messages()
        assert len(messages) == 2
        assert messages[0]["role"] == "user"
        assert messages[1]["content"] == "Hi there"
    
    def test_message_limit(self) -> None:
        """Test that messages are trimmed at limit."""
        memory = AgentMemory(agent_name="test", max_short_term=3)
        
        for i in range(5):
            memory.add_message("user", f"Message {i}")
        
        messages = memory.get_recent_messages(limit=10)
        assert len(messages) == 3
        assert messages[0]["content"] == "Message 2"
    
    def test_search(self) -> None:
        """Test memory search."""
        memory = AgentMemory(agent_name="test")
        memory._entries.append(MemoryEntry(
            content="Python is great",
            entry_type="thought",
        ))
        memory._entries.append(MemoryEntry(
            content="JavaScript is also good",
            entry_type="thought",
        ))
        
        results = memory.search("Python")
        assert len(results) == 1
        assert "Python" in str(results[0].content)


class TestAgentMessage:
    """Tests for AgentMessage class."""
    
    def test_create_message(self) -> None:
        """Test message creation."""
        msg = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            message_type=MessageType.REQUEST,
            content={"task": "do something"},
            confidence=0.9,
        )
        
        assert msg.sender == "agent_a"
        assert msg.receiver == "agent_b"
        assert msg.message_type == MessageType.REQUEST
        assert msg.priority == Priority.NORMAL
        assert msg.message_id is not None
    
    def test_create_reply(self) -> None:
        """Test creating a reply message."""
        original = AgentMessage(
            sender="agent_a",
            receiver="agent_b",
            message_type=MessageType.REQUEST,
            content="help",
            confidence=1.0,
        )
        
        reply = original.create_reply(
            sender="agent_b",
            content="here's help",
            message_type=MessageType.RESPONSE,
        )
        
        assert reply.sender == "agent_b"
        assert reply.receiver == "agent_a"
        assert reply.in_reply_to == original.message_id


class TestConsensusBuilder:
    """Tests for ConsensusBuilder class."""
    
    def test_simple_approval(self) -> None:
        """Test basic approval consensus."""
        consensus = ConsensusBuilder(
            decision_id="test_1",
            topic="Test decision",
            required_approvals=2,
        )
        
        consensus.add_vote(Vote(
            voter="agent_a",
            vote_type=VoteType.APPROVE,
            confidence=1.0,  # Full confidence
            reasoning="Looks good",
        ))
        
        consensus.add_vote(Vote(
            voter="agent_b",
            vote_type=VoteType.APPROVE,
            confidence=1.0,  # Full confidence
            reasoning="I agree",
        ))
        
        result = consensus.get_result()
        assert result.approved is True
        assert len(result.votes) == 2
    
    def test_security_veto(self) -> None:
        """Test that security agent can veto."""
        consensus = ConsensusBuilder(
            decision_id="test_2",
            topic="Change that might be insecure",
            required_approvals=2,
            allow_veto=True,
        )
        
        consensus.add_vote(Vote(
            voter="development_agent",
            vote_type=VoteType.APPROVE,
            confidence=0.9,
            reasoning="Code works",
        ))
        
        consensus.add_vote(Vote(
            voter="security_agent",
            vote_type=VoteType.REJECT,
            confidence=0.95,
            reasoning="SQL injection vulnerability",
            concerns=["SQL injection in user input"],
        ))
        
        result = consensus.get_result()
        assert result.approved is False
        assert "veto" in result.final_decision.lower()
    
    def test_duplicate_vote_ignored(self) -> None:
        """Test that duplicate votes are ignored."""
        consensus = ConsensusBuilder(
            decision_id="test_3",
            topic="Test",
            required_approvals=2,
        )
        
        consensus.add_vote(Vote(
            voter="agent_a",
            vote_type=VoteType.APPROVE,
            confidence=0.9,
            reasoning="First vote",
        ))
        
        consensus.add_vote(Vote(
            voter="agent_a",
            vote_type=VoteType.REJECT,
            confidence=0.9,
            reasoning="Changed my mind",
        ))
        
        assert len(consensus._votes) == 1
        assert consensus._votes[0].vote_type == VoteType.APPROVE
    
    def test_pending_count(self) -> None:
        """Test pending votes count."""
        consensus = ConsensusBuilder(
            decision_id="test_4",
            topic="Test",
            required_approvals=3,
        )
        
        assert consensus.pending_count == 3
        
        consensus.add_vote(Vote(
            voter="agent_a",
            vote_type=VoteType.APPROVE,
            confidence=0.9,
            reasoning="Ok",
        ))
        
        assert consensus.pending_count == 2
