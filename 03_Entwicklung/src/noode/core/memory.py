"""Agent Memory system for Noode.

Provides short-term (conversation) and long-term (knowledge base) memory
for agents to maintain context and learn from experience.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

import structlog

if TYPE_CHECKING:
    from noode.core.base_agent import Insight, Thought

logger = structlog.get_logger()


@dataclass
class MemoryEntry:
    """A single memory entry."""
    
    content: Any
    entry_type: str  # thought, insight, action, message
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 0.5
    tags: list[str] = field(default_factory=list)


class AgentMemory:
    """Memory system for an agent.
    
    Maintains:
    - Conversation history (short-term)
    - Thoughts and insights (medium-term)
    - Learned patterns (long-term, persisted)
    
    Attributes:
        agent_name: Name of the owning agent
        max_short_term: Maximum entries in short-term memory
    """
    
    def __init__(
        self,
        agent_name: str,
        max_short_term: int = 100,
    ) -> None:
        """Initialize agent memory.
        
        Args:
            agent_name: Name of the agent this memory belongs to
            max_short_term: Max entries to keep in short-term memory
        """
        self.agent_name = agent_name
        self.max_short_term = max_short_term
        
        # Short-term memory (conversation)
        self._messages: list[dict[str, str]] = []
        
        # Medium-term memory (thoughts, insights)
        self._thoughts: list["Thought"] = []
        self._insights: list["Insight"] = []
        
        # Long-term memory entries
        self._entries: list[MemoryEntry] = []
        
        logger.debug("memory_initialized", agent=agent_name)
    
    def add_message(self, role: str, content: str) -> None:
        """Add a conversation message.
        
        Args:
            role: Message role (user, assistant, system)
            content: Message content
        """
        self._messages.append({"role": role, "content": content})
        
        # Trim if exceeds limit
        if len(self._messages) > self.max_short_term:
            self._messages = self._messages[-self.max_short_term:]
    
    def get_recent_messages(self, limit: int = 10) -> list[dict[str, str]]:
        """Get recent conversation messages.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of recent messages
        """
        return self._messages[-limit:]
    
    def add_thought(self, thought: "Thought") -> None:
        """Record a thought.
        
        Args:
            thought: The thought to record
        """
        self._thoughts.append(thought)
        self._entries.append(MemoryEntry(
            content=thought,
            entry_type="thought",
            importance=thought.confidence,
        ))
    
    def add_insight(self, insight: "Insight") -> None:
        """Record an insight.
        
        Args:
            insight: The insight to record
        """
        self._insights.append(insight)
        self._entries.append(MemoryEntry(
            content=insight,
            entry_type="insight",
            importance=1.0 if insight.should_update_knowledge else 0.5,
        ))
    
    def get_context_summary(self) -> str:
        """Generate a summary of current context.
        
        Returns:
            String summary of relevant memory context
        """
        parts = []
        
        # Recent thoughts
        if self._thoughts:
            recent_thoughts = self._thoughts[-3:]
            parts.append("Recent thoughts:")
            for t in recent_thoughts:
                parts.append(f"  - {t.content[:100]}... (conf: {t.confidence:.1f})")
        
        # Recent insights
        if self._insights:
            recent_insights = self._insights[-3:]
            parts.append("\nRecent insights:")
            for i in recent_insights:
                parts.append(f"  - {i.lesson[:100]}...")
        
        # Conversation summary
        if self._messages:
            parts.append(f"\nConversation: {len(self._messages)} messages")
        
        return "\n".join(parts) if parts else "No context yet."
    
    def search(
        self,
        query: str,
        entry_type: str | None = None,
        limit: int = 5,
    ) -> list[MemoryEntry]:
        """Search memory entries.
        
        Args:
            query: Search query (simple keyword matching for now)
            entry_type: Optional filter by entry type
            limit: Maximum results to return
            
        Returns:
            Matching memory entries
        """
        results = []
        
        for entry in reversed(self._entries):
            if entry_type and entry.entry_type != entry_type:
                continue
            
            # Simple keyword matching (would use embeddings in production)
            content_str = str(entry.content).lower()
            if query.lower() in content_str:
                results.append(entry)
                if len(results) >= limit:
                    break
        
        return results
    
    def clear_short_term(self) -> None:
        """Clear short-term conversation memory."""
        self._messages.clear()
        logger.debug("short_term_cleared", agent=self.agent_name)
    
    async def persist(self, path: str) -> None:
        """Persist memory to disk.
        
        Args:
            path: Path to save memory data
        """
        import json
        from pathlib import Path
        
        data = {
            "agent_name": self.agent_name,
            "entries": [
                {
                    "content": str(e.content),
                    "entry_type": e.entry_type,
                    "timestamp": e.timestamp.isoformat(),
                    "importance": e.importance,
                    "tags": e.tags,
                }
                for e in self._entries
            ],
        }
        
        Path(path).write_text(json.dumps(data, indent=2))
        logger.info("memory_persisted", agent=self.agent_name, path=path)
    
    async def load(self, path: str) -> None:
        """Load memory from disk.
        
        Args:
            path: Path to load memory data from
        """
        import json
        from pathlib import Path
        
        data = json.loads(Path(path).read_text())
        
        self._entries = [
            MemoryEntry(
                content=e["content"],
                entry_type=e["entry_type"],
                timestamp=datetime.fromisoformat(e["timestamp"]),
                importance=e["importance"],
                tags=e["tags"],
            )
            for e in data.get("entries", [])
        ]
        
        logger.info("memory_loaded", agent=self.agent_name, entries=len(self._entries))
