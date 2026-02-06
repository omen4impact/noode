"""Message types and structures for inter-agent communication."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class MessageType(Enum):
    """Types of messages agents can exchange."""
    
    REQUEST = "request"       # Ask another agent to do something
    RESPONSE = "response"     # Reply to a request
    ESCALATION = "escalation" # Escalate to orchestrator/human
    BROADCAST = "broadcast"   # Inform all agents
    REVIEW = "review"         # Request peer review
    APPROVAL = "approval"     # Approve a change
    REJECTION = "rejection"   # Reject a change
    STATUS = "status"         # Status update


class Priority(Enum):
    """Message priority levels."""
    
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentMessage:
    """A message between agents.
    
    Attributes:
        sender: Name of sending agent
        receiver: Name of receiving agent (or "broadcast")
        message_type: Type of message
        content: Message payload
        confidence: Sender's confidence in the message
        timestamp: When message was created
        priority: Message priority
        correlation_id: ID linking related messages
        in_reply_to: ID of message this replies to
    """
    
    sender: str
    receiver: str
    message_type: MessageType
    content: Any
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.NORMAL
    correlation_id: str | None = None
    in_reply_to: str | None = None
    message_id: str = field(default_factory=lambda: _generate_id())
    
    def create_reply(
        self,
        sender: str,
        content: Any,
        message_type: MessageType = MessageType.RESPONSE,
        confidence: float = 1.0,
    ) -> "AgentMessage":
        """Create a reply to this message.
        
        Args:
            sender: Name of replying agent
            content: Reply content
            message_type: Type of reply
            confidence: Confidence in reply
            
        Returns:
            New message as reply
        """
        return AgentMessage(
            sender=sender,
            receiver=self.sender,
            message_type=message_type,
            content=content,
            confidence=confidence,
            correlation_id=self.correlation_id or self.message_id,
            in_reply_to=self.message_id,
        )


@dataclass
class TaskRequest:
    """Request for an agent to perform a task."""
    
    task_id: str
    task_type: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    deadline: datetime | None = None
    dependencies: list[str] = field(default_factory=list)


@dataclass
class TaskResult:
    """Result of a completed task."""
    
    task_id: str
    success: bool
    output: Any
    artifacts: list[str] = field(default_factory=list)
    error: str | None = None
    metrics: dict[str, float] = field(default_factory=dict)


@dataclass 
class ReviewRequest:
    """Request for peer review."""
    
    change_id: str
    change_type: str  # code, config, schema, etc.
    description: str
    diff: str
    files_changed: list[str]
    author: str
    reviewers_needed: int = 2


@dataclass
class ReviewResult:
    """Result of a peer review."""
    
    change_id: str
    reviewer: str
    approved: bool
    comments: list[str] = field(default_factory=list)
    required_changes: list[str] = field(default_factory=list)
    security_concerns: list[str] = field(default_factory=list)


def _generate_id() -> str:
    """Generate a unique message ID."""
    import uuid
    return str(uuid.uuid4())[:8]
