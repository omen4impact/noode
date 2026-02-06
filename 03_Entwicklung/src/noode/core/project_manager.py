"""Multi-project management for Noode.

Allows managing multiple projects with isolated contexts.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

import structlog

logger = structlog.get_logger()


@dataclass
class ProjectConfig:
    """Configuration for a project."""
    
    name: str
    template: str = "web-app"
    version: str = "0.1.0"
    agents: dict[str, dict[str, Any]] = field(default_factory=dict)
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class Project:
    """A Noode project."""
    
    project_id: str
    name: str
    path: Path
    config: ProjectConfig
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict."""
        return {
            "project_id": self.project_id,
            "name": self.name,
            "path": str(self.path),
            "config": {
                "name": self.config.name,
                "template": self.config.template,
                "version": self.config.version,
                "agents": self.config.agents,
                "settings": self.config.settings,
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        """Deserialize from dict."""
        return cls(
            project_id=data["project_id"],
            name=data["name"],
            path=Path(data["path"]),
            config=ProjectConfig(
                name=data["config"]["name"],
                template=data["config"].get("template", "web-app"),
                version=data["config"].get("version", "0.1.0"),
                agents=data["config"].get("agents", {}),
                settings=data["config"].get("settings", {}),
            ),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            is_active=data.get("is_active", True),
        )


class ProjectManager:
    """Manage multiple projects."""
    
    def __init__(
        self,
        workspace_path: Path | None = None,
    ) -> None:
        """Initialize project manager.
        
        Args:
            workspace_path: Path for storing project metadata
        """
        self.workspace_path = workspace_path or Path.home() / ".noode" / "projects"
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        
        self._projects: dict[str, Project] = {}
        self._active_project_id: str | None = None
        
        self._load_projects()
    
    def create_project(
        self,
        name: str,
        path: Path,
        template: str = "web-app",
        config: dict[str, Any] | None = None,
    ) -> Project:
        """Create a new project.
        
        Args:
            name: Project name
            path: Project directory path
            template: Project template
            config: Additional configuration
            
        Returns:
            Created project
        """
        project_id = str(uuid4())[:12]
        now = datetime.now()
        
        project_config = ProjectConfig(
            name=name,
            template=template,
            version="0.1.0",
            agents=config.get("agents", {}) if config else {},
            settings=config.get("settings", {}) if config else {},
        )
        
        project = Project(
            project_id=project_id,
            name=name,
            path=path,
            config=project_config,
            created_at=now,
            updated_at=now,
        )
        
        self._projects[project_id] = project
        self._save_project(project)
        
        logger.info(
            "project_created",
            project_id=project_id,
            name=name,
        )
        
        return project
    
    def get_project(self, project_id: str) -> Project | None:
        """Get a project by ID.
        
        Args:
            project_id: Project ID
            
        Returns:
            Project or None
        """
        return self._projects.get(project_id)
    
    def get_project_by_name(self, name: str) -> Project | None:
        """Get a project by name.
        
        Args:
            name: Project name
            
        Returns:
            Project or None
        """
        for project in self._projects.values():
            if project.name == name:
                return project
        return None
    
    def get_project_by_path(self, path: Path) -> Project | None:
        """Get a project by path.
        
        Args:
            path: Project path
            
        Returns:
            Project or None
        """
        for project in self._projects.values():
            if project.path == path:
                return project
        return None
    
    def update_project(
        self,
        project_id: str,
        name: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> Project | None:
        """Update a project.
        
        Args:
            project_id: Project ID
            name: New name
            config: Config updates
            
        Returns:
            Updated project or None
        """
        project = self._projects.get(project_id)
        if not project:
            return None
        
        if name:
            project.name = name
            project.config.name = name
        
        if config:
            if "agents" in config:
                project.config.agents.update(config["agents"])
            if "settings" in config:
                project.config.settings.update(config["settings"])
            if "version" in config:
                project.config.version = config["version"]
        
        project.updated_at = datetime.now()
        self._save_project(project)
        
        return project
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project (metadata only, not files).
        
        Args:
            project_id: Project ID
            
        Returns:
            True if deleted
        """
        if project_id not in self._projects:
            return False
        
        project = self._projects[project_id]
        project.is_active = False
        self._save_project(project)
        
        del self._projects[project_id]
        
        if self._active_project_id == project_id:
            self._active_project_id = None
        
        logger.info("project_deleted", project_id=project_id)
        
        return True
    
    def list_projects(
        self,
        active_only: bool = True,
    ) -> list[Project]:
        """List all projects.
        
        Args:
            active_only: Only show active projects
            
        Returns:
            List of projects
        """
        projects = list(self._projects.values())
        
        if active_only:
            projects = [p for p in projects if p.is_active]
        
        return sorted(projects, key=lambda p: p.updated_at, reverse=True)
    
    def set_active(self, project_id: str) -> bool:
        """Set the active project.
        
        Args:
            project_id: Project ID to activate
            
        Returns:
            True if set
        """
        if project_id not in self._projects:
            return False
        
        self._active_project_id = project_id
        
        logger.info("active_project_changed", project_id=project_id)
        
        return True
    
    def get_active(self) -> Project | None:
        """Get the active project.
        
        Returns:
            Active project or None
        """
        if self._active_project_id:
            return self._projects.get(self._active_project_id)
        return None
    
    def detect_project(self, path: Path | None = None) -> Project | None:
        """Detect project from current directory.
        
        Args:
            path: Path to check (defaults to cwd)
            
        Returns:
            Detected project or None
        """
        check_path = path or Path.cwd()
        
        # Check if path is a known project
        for project in self._projects.values():
            if check_path == project.path or project.path in check_path.parents:
                return project
        
        # Check for noode.yaml in path or parents
        current = check_path
        while current != current.parent:
            if (current / "noode.yaml").exists():
                return self.get_project_by_path(current)
            current = current.parent
        
        return None
    
    def get_stats(self) -> dict[str, Any]:
        """Get project statistics.
        
        Returns:
            Statistics dict
        """
        active = [p for p in self._projects.values() if p.is_active]
        
        by_template: dict[str, int] = {}
        for project in active:
            template = project.config.template
            by_template[template] = by_template.get(template, 0) + 1
        
        return {
            "total_projects": len(self._projects),
            "active_projects": len(active),
            "by_template": by_template,
            "active_project_id": self._active_project_id,
        }
    
    def _save_project(self, project: Project) -> None:
        """Save project metadata."""
        project_file = self.workspace_path / f"{project.project_id}.json"
        project_file.write_text(json.dumps(project.to_dict(), indent=2))
    
    def _load_projects(self) -> None:
        """Load all projects from disk."""
        for project_file in self.workspace_path.glob("*.json"):
            try:
                data = json.loads(project_file.read_text())
                project = Project.from_dict(data)
                if project.is_active:
                    self._projects[project.project_id] = project
            except Exception as e:
                logger.warning(
                    "project_load_failed",
                    file=str(project_file),
                    error=str(e),
                )
        
        logger.info("projects_loaded", count=len(self._projects))
