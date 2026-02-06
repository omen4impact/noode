"""Plugin system for Noode agents.

Allows extending the platform with custom agents and capabilities.
"""

import importlib
import importlib.util
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import structlog

from noode.core.base_agent import BaseAgent

logger = structlog.get_logger()


@dataclass
class PluginMetadata:
    """Metadata for a plugin."""
    
    name: str
    version: str
    description: str
    author: str = ""
    homepage: str = ""
    dependencies: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)


class Plugin(ABC):
    """Base class for all plugins."""
    
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        pass
    
    @abstractmethod
    def initialize(self, context: dict[str, Any]) -> None:
        """Initialize the plugin with context."""
        pass
    
    @abstractmethod
    def shutdown(self) -> None:
        """Clean up plugin resources."""
        pass


class AgentPlugin(Plugin):
    """Plugin that provides a custom agent."""
    
    @abstractmethod
    def get_agent(self) -> BaseAgent:
        """Return the agent instance."""
        pass


class ToolPlugin(Plugin):
    """Plugin that provides additional tools."""
    
    @abstractmethod
    def get_tools(self) -> dict[str, Callable]:
        """Return dict of tool name -> callable."""
        pass


class MiddlewarePlugin(Plugin):
    """Plugin that intercepts and modifies requests/responses."""
    
    @abstractmethod
    async def pre_process(self, request: dict[str, Any]) -> dict[str, Any]:
        """Process request before agent handles it."""
        pass
    
    @abstractmethod
    async def post_process(
        self,
        request: dict[str, Any],
        response: dict[str, Any],
    ) -> dict[str, Any]:
        """Process response after agent returns it."""
        pass


@dataclass
class LoadedPlugin:
    """A loaded plugin instance."""
    
    metadata: PluginMetadata
    instance: Plugin
    enabled: bool = True


class PluginManager:
    """Manage plugin lifecycle."""
    
    def __init__(
        self,
        plugin_dirs: list[Path] | None = None,
    ) -> None:
        """Initialize plugin manager.
        
        Args:
            plugin_dirs: Directories to search for plugins
        """
        self.plugin_dirs = plugin_dirs or []
        self._plugins: dict[str, LoadedPlugin] = {}
        self._hooks: dict[str, list[Callable]] = {}
    
    def discover(self) -> list[PluginMetadata]:
        """Discover available plugins.
        
        Returns:
            List of discovered plugin metadata
        """
        discovered = []
        
        for plugin_dir in self.plugin_dirs:
            if not plugin_dir.exists():
                continue
            
            for path in plugin_dir.glob("*/plugin.py"):
                try:
                    metadata = self._load_metadata(path)
                    if metadata:
                        discovered.append(metadata)
                except Exception as e:
                    logger.warning(
                        "plugin_discovery_failed",
                        path=str(path),
                        error=str(e),
                    )
        
        return discovered
    
    def load(self, plugin_name: str) -> LoadedPlugin | None:
        """Load a plugin by name.
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            Loaded plugin or None
        """
        if plugin_name in self._plugins:
            return self._plugins[plugin_name]
        
        for plugin_dir in self.plugin_dirs:
            plugin_path = plugin_dir / plugin_name / "plugin.py"
            
            if plugin_path.exists():
                try:
                    plugin = self._load_plugin(plugin_path)
                    if plugin:
                        loaded = LoadedPlugin(
                            metadata=plugin.metadata,
                            instance=plugin,
                        )
                        self._plugins[plugin_name] = loaded
                        
                        # Initialize plugin
                        plugin.initialize({"manager": self})
                        
                        logger.info(
                            "plugin_loaded",
                            name=plugin_name,
                            version=plugin.metadata.version,
                        )
                        
                        return loaded
                except Exception as e:
                    logger.error(
                        "plugin_load_failed",
                        name=plugin_name,
                        error=str(e),
                    )
        
        return None
    
    def unload(self, plugin_name: str) -> bool:
        """Unload a plugin.
        
        Args:
            plugin_name: Name of plugin to unload
            
        Returns:
            True if unloaded
        """
        if plugin_name not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_name]
        
        try:
            plugin.instance.shutdown()
        except Exception as e:
            logger.warning("plugin_shutdown_error", name=plugin_name, error=str(e))
        
        del self._plugins[plugin_name]
        
        logger.info("plugin_unloaded", name=plugin_name)
        
        return True
    
    def get_agents(self) -> list[BaseAgent]:
        """Get all agents from loaded plugins.
        
        Returns:
            List of agent instances
        """
        agents = []
        
        for loaded in self._plugins.values():
            if isinstance(loaded.instance, AgentPlugin) and loaded.enabled:
                try:
                    agents.append(loaded.instance.get_agent())
                except Exception as e:
                    logger.error(
                        "agent_plugin_error",
                        name=loaded.metadata.name,
                        error=str(e),
                    )
        
        return agents
    
    def get_tools(self) -> dict[str, Callable]:
        """Get all tools from loaded plugins.
        
        Returns:
            Dict of tool name -> callable
        """
        tools = {}
        
        for loaded in self._plugins.values():
            if isinstance(loaded.instance, ToolPlugin) and loaded.enabled:
                try:
                    tools.update(loaded.instance.get_tools())
                except Exception as e:
                    logger.error(
                        "tool_plugin_error",
                        name=loaded.metadata.name,
                        error=str(e),
                    )
        
        return tools
    
    async def apply_middleware(
        self,
        request: dict[str, Any],
        handler: Callable,
    ) -> dict[str, Any]:
        """Apply middleware plugins to a request.
        
        Args:
            request: The request to process
            handler: The actual handler function
            
        Returns:
            Processed response
        """
        # Pre-process
        for loaded in self._plugins.values():
            if isinstance(loaded.instance, MiddlewarePlugin) and loaded.enabled:
                request = await loaded.instance.pre_process(request)
        
        # Handle
        response = await handler(request)
        
        # Post-process
        for loaded in self._plugins.values():
            if isinstance(loaded.instance, MiddlewarePlugin) and loaded.enabled:
                response = await loaded.instance.post_process(request, response)
        
        return response
    
    def register_hook(self, event: str, callback: Callable) -> None:
        """Register a hook callback.
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)
    
    async def emit(self, event: str, data: Any = None) -> None:
        """Emit an event to all registered hooks.
        
        Args:
            event: Event name
            data: Event data
        """
        for callback in self._hooks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    callback(data)
            except Exception as e:
                logger.error("hook_error", event=event, error=str(e))
    
    def list_plugins(self) -> list[dict[str, Any]]:
        """List all loaded plugins.
        
        Returns:
            List of plugin info dicts
        """
        return [
            {
                "name": loaded.metadata.name,
                "version": loaded.metadata.version,
                "description": loaded.metadata.description,
                "enabled": loaded.enabled,
                "type": type(loaded.instance).__name__,
            }
            for loaded in self._plugins.values()
        ]
    
    def enable(self, plugin_name: str) -> bool:
        """Enable a plugin.
        
        Args:
            plugin_name: Plugin to enable
            
        Returns:
            True if enabled
        """
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = True
            return True
        return False
    
    def disable(self, plugin_name: str) -> bool:
        """Disable a plugin.
        
        Args:
            plugin_name: Plugin to disable
            
        Returns:
            True if disabled
        """
        if plugin_name in self._plugins:
            self._plugins[plugin_name].enabled = False
            return True
        return False
    
    def _load_metadata(self, path: Path) -> PluginMetadata | None:
        """Load plugin metadata from file."""
        spec = importlib.util.spec_from_file_location("plugin", path)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, "PLUGIN_METADATA"):
            data = module.PLUGIN_METADATA
            return PluginMetadata(
                name=data.get("name", path.parent.name),
                version=data.get("version", "0.0.1"),
                description=data.get("description", ""),
                author=data.get("author", ""),
                homepage=data.get("homepage", ""),
                dependencies=data.get("dependencies", []),
                capabilities=data.get("capabilities", []),
            )
        
        return None
    
    def _load_plugin(self, path: Path) -> Plugin | None:
        """Load a plugin from file."""
        spec = importlib.util.spec_from_file_location("plugin", path)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find Plugin subclass
        for name in dir(module):
            obj = getattr(module, name)
            if (
                isinstance(obj, type) and
                issubclass(obj, Plugin) and
                obj is not Plugin and
                obj is not AgentPlugin and
                obj is not ToolPlugin and
                obj is not MiddlewarePlugin
            ):
                return obj()
        
        return None


# Import asyncio for emit function
import asyncio
