"""Example plugin: Custom Logger Agent.

Shows how to create a custom agent plugin.
"""

from typing import Any
from datetime import datetime

from noode.plugins import AgentPlugin, PluginMetadata
from noode.core.base_agent import BaseAgent, Action, Result


PLUGIN_METADATA = {
    "name": "logger-agent",
    "version": "1.0.0",
    "description": "An agent that logs all activities",
    "author": "Noode Team",
    "capabilities": ["logging", "monitoring"],
}


class LoggerAgent(BaseAgent):
    """Agent that logs all activities."""
    
    def __init__(self) -> None:
        super().__init__(
            name="logger_agent",
            role="Activity Logger",
            capabilities=["logging", "monitoring", "audit"],
            model="gpt-4o-mini",  # Lightweight model
            confidence_threshold=0.5,
        )
        self.log_entries: list[dict[str, Any]] = []
    
    async def act(self, action: Action) -> Result:
        """Log the action."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action.action_type,
            "parameters": action.parameters,
        }
        self.log_entries.append(entry)
        
        return Result(
            success=True,
            output={"logged": True, "entry_count": len(self.log_entries)},
        )
    
    def get_logs(self) -> list[dict[str, Any]]:
        """Get all log entries."""
        return self.log_entries.copy()


class LoggerAgentPlugin(AgentPlugin):
    """Plugin that provides the logger agent."""
    
    def __init__(self) -> None:
        self._agent: LoggerAgent | None = None
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name=PLUGIN_METADATA["name"],
            version=PLUGIN_METADATA["version"],
            description=PLUGIN_METADATA["description"],
            author=PLUGIN_METADATA["author"],
            capabilities=PLUGIN_METADATA["capabilities"],
        )
    
    def initialize(self, context: dict[str, Any]) -> None:
        """Initialize the plugin."""
        self._agent = LoggerAgent()
    
    def shutdown(self) -> None:
        """Clean up."""
        if self._agent:
            # Save logs if needed
            pass
    
    def get_agent(self) -> BaseAgent:
        """Return the logger agent."""
        if not self._agent:
            self._agent = LoggerAgent()
        return self._agent
