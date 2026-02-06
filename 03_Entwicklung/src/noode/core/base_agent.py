"""Base Agent implementation for Noode.

This module provides the foundational BaseAgent class that all specialized
agents inherit from. It implements the core think-act-reflect loop with
LLM integration via LiteLLM.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import litellm
import structlog

from noode.core.memory import AgentMemory
from noode.protocols.messages import AgentMessage, MessageType

logger = structlog.get_logger()


class AgentState(Enum):
    """Current state of an agent."""
    
    IDLE = "idle"
    THINKING = "thinking"
    ACTING = "acting"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class Thought:
    """Represents an agent's reasoning process."""
    
    content: str
    confidence: float
    reasoning_steps: list[str] = field(default_factory=list)
    requires_research: bool = False
    requires_escalation: bool = False


@dataclass
class Action:
    """Represents an action to be executed by an agent."""
    
    action_type: str
    parameters: dict[str, Any]
    description: str
    risk_level: str = "low"  # low, medium, high, critical


@dataclass
class Result:
    """Result of an agent action."""
    
    success: bool
    output: Any
    error: str | None = None
    duration_ms: float = 0.0
    artifacts: list[str] = field(default_factory=list)


@dataclass
class Insight:
    """Insight gained from reflecting on a result."""
    
    lesson: str
    should_update_knowledge: bool
    pattern_identified: str | None = None
    improvement_suggestion: str | None = None


class BaseAgent(ABC):
    """Base class for all Noode agents.
    
    Implements the core agent loop:
    1. Think - Analyze the task and plan approach
    2. Act - Execute planned actions
    3. Reflect - Learn from results
    
    Attributes:
        name: Unique identifier for the agent
        role: Description of agent's specialization
        capabilities: List of things this agent can do
        confidence_threshold: Minimum confidence to proceed autonomously
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        capabilities: list[str],
        model: str = "gpt-4o",
        confidence_threshold: float = 0.7,
    ) -> None:
        """Initialize the agent.
        
        Args:
            name: Unique name for this agent instance
            role: Description of the agent's role/specialization  
            capabilities: List of capabilities this agent has
            model: LLM model to use (via LiteLLM)
            confidence_threshold: Minimum confidence to act autonomously
        """
        self.name = name
        self.role = role
        self.capabilities = capabilities
        self.model = model
        self.confidence_threshold = confidence_threshold
        self.state = AgentState.IDLE
        self.memory = AgentMemory(agent_name=name)
        self._message_queue: list[AgentMessage] = []
        
        logger.info(
            "agent_initialized",
            agent=name,
            role=role,
            capabilities=capabilities,
        )
    
    @property
    def system_prompt(self) -> str:
        """Generate the system prompt for this agent."""
        return f"""You are {self.name}, a specialized AI agent.

Role: {self.role}

Capabilities:
{chr(10).join(f'- {cap}' for cap in self.capabilities)}

Guidelines:
1. Always think systematically before acting
2. Research current best practices before implementation
3. Escalate when confidence is below {self.confidence_threshold}
4. Document your reasoning clearly
5. Consider security implications at all times

Current context from memory:
{self.memory.get_context_summary()}
"""
    
    async def think(self, prompt: str) -> Thought:
        """Analyze a task and plan approach.
        
        Args:
            prompt: The task or question to think about
            
        Returns:
            Thought object with analysis and confidence
        """
        self.state = AgentState.THINKING
        
        logger.info("agent_thinking", agent=self.name, prompt=prompt[:100])
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Analyze this task and plan your approach:

{prompt}

Respond with:
1. Your understanding of the task
2. Step-by-step reasoning
3. Confidence level (0.0-1.0)
4. Whether you need more research
5. Whether this should be escalated"""},
        ]
        
        # Add conversation history
        for msg in self.memory.get_recent_messages(limit=10):
            messages.insert(-1, msg)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=messages,
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        
        # Parse response (simplified - would use structured output in production)
        thought = Thought(
            content=content,
            confidence=self._extract_confidence(content),
            reasoning_steps=self._extract_steps(content),
            requires_research="research" in content.lower() and "need" in content.lower(),
            requires_escalation="escalate" in content.lower(),
        )
        
        self.memory.add_thought(thought)
        self.state = AgentState.IDLE
        
        return thought
    
    @abstractmethod
    async def act(self, action: Action) -> Result:
        """Execute an action. Must be implemented by subclasses.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the action
        """
        pass
    
    async def reflect(self, result: Result) -> Insight:
        """Reflect on the result of an action.
        
        Args:
            result: The result to reflect on
            
        Returns:
            Insight gained from reflection
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"""Reflect on this result:

Success: {result.success}
Output: {result.output}
Error: {result.error}
Duration: {result.duration_ms}ms

What can we learn? Should we update our knowledge base?
Identify any patterns or improvement opportunities."""},
        ]
        
        response = await litellm.acompletion(
            model=self.model,
            messages=messages,
            temperature=0.5,
        )
        
        content = response.choices[0].message.content or ""
        
        insight = Insight(
            lesson=content,
            should_update_knowledge=not result.success or "pattern" in content.lower(),
            pattern_identified=self._extract_pattern(content),
        )
        
        self.memory.add_insight(insight)
        
        return insight
    
    async def escalate(self, reason: str) -> AgentMessage:
        """Escalate to orchestrator or human.
        
        Args:
            reason: Why escalation is needed
            
        Returns:
            Escalation message
        """
        logger.warning("agent_escalating", agent=self.name, reason=reason)
        
        return AgentMessage(
            sender=self.name,
            receiver="orchestrator",
            message_type=MessageType.ESCALATION,
            content={"reason": reason, "context": self.memory.get_context_summary()},
            confidence=0.0,
            timestamp=datetime.now(),
        )
    
    def receive_message(self, message: AgentMessage) -> None:
        """Receive a message from another agent.
        
        Args:
            message: The message to receive
        """
        self._message_queue.append(message)
        logger.info(
            "message_received",
            agent=self.name,
            sender=message.sender,
            type=message.message_type.value,
        )
    
    async def send_message(
        self,
        receiver: str,
        content: Any,
        message_type: MessageType = MessageType.REQUEST,
        confidence: float = 1.0,
    ) -> AgentMessage:
        """Send a message to another agent.
        
        Args:
            receiver: Name of receiving agent
            content: Message content
            message_type: Type of message
            confidence: Confidence in the message
            
        Returns:
            The sent message
        """
        message = AgentMessage(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            content=content,
            confidence=confidence,
            timestamp=datetime.now(),
        )
        
        logger.info(
            "message_sent",
            agent=self.name,
            receiver=receiver,
            type=message_type.value,
        )
        
        return message
    
    def _extract_confidence(self, content: str) -> float:
        """Extract confidence value from LLM response."""
        import re
        
        # Look for patterns like "confidence: 0.8" or "85%"
        patterns = [
            r"confidence[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*%",
            r"(\d+\.?\d*)\s*/\s*1",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                value = float(match.group(1))
                return value / 100 if value > 1 else value
        
        return 0.5  # Default medium confidence
    
    def _extract_steps(self, content: str) -> list[str]:
        """Extract reasoning steps from LLM response."""
        import re
        
        # Look for numbered or bulleted lists
        steps = re.findall(r"^\s*(?:\d+\.|[-*])\s*(.+)$", content, re.MULTILINE)
        return steps[:10]  # Limit to 10 steps
    
    def _extract_pattern(self, content: str) -> str | None:
        """Extract identified pattern from reflection."""
        if "pattern" in content.lower():
            # Simplified extraction
            lines = content.split("\n")
            for line in lines:
                if "pattern" in line.lower():
                    return line.strip()
        return None
