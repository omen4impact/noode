"""Tests for Sprint 4 components."""

import pytest
from pathlib import Path
import tempfile
from datetime import datetime

from noode.core.project_manager import ProjectManager, Project, ProjectConfig
from noode.plugins.manager import PluginManager, PluginMetadata
from noode.cicd.generator import CICDGenerator


class TestProjectManager:
    """Tests for ProjectManager."""
    
    def test_init(self) -> None:
        """Test initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            assert len(manager._projects) == 0
    
    def test_create_project(self) -> None:
        """Test project creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            project = manager.create_project(
                name="test-project",
                path=Path(tmpdir) / "test-project",
                template="web-app",
            )
            
            assert project.name == "test-project"
            assert project.config.template == "web-app"
            assert project.is_active is True
    
    def test_get_project(self) -> None:
        """Test project retrieval by ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            created = manager.create_project(
                name="test",
                path=Path(tmpdir) / "test",
            )
            
            retrieved = manager.get_project(created.project_id)
            assert retrieved is not None
            assert retrieved.name == "test"
    
    def test_get_project_by_name(self) -> None:
        """Test project retrieval by name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            manager.create_project(name="my-app", path=Path(tmpdir) / "my-app")
            
            project = manager.get_project_by_name("my-app")
            assert project is not None
            assert project.name == "my-app"
    
    def test_update_project(self) -> None:
        """Test project update."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            project = manager.create_project(
                name="old-name",
                path=Path(tmpdir) / "project",
            )
            
            updated = manager.update_project(
                project.project_id,
                name="new-name",
                config={"version": "1.0.0"},
            )
            
            assert updated is not None
            assert updated.name == "new-name"
            assert updated.config.version == "1.0.0"
    
    def test_delete_project(self) -> None:
        """Test project deletion."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            project = manager.create_project(
                name="to-delete",
                path=Path(tmpdir) / "to-delete",
            )
            
            result = manager.delete_project(project.project_id)
            assert result is True
            assert manager.get_project(project.project_id) is None
    
    def test_list_projects(self) -> None:
        """Test project listing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            manager.create_project(name="p1", path=Path(tmpdir) / "p1")
            manager.create_project(name="p2", path=Path(tmpdir) / "p2")
            
            projects = manager.list_projects()
            assert len(projects) == 2
    
    def test_set_active(self) -> None:
        """Test setting active project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            project = manager.create_project(
                name="active",
                path=Path(tmpdir) / "active",
            )
            
            result = manager.set_active(project.project_id)
            assert result is True
            assert manager.get_active() == project
    
    def test_get_stats(self) -> None:
        """Test statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = ProjectManager(workspace_path=Path(tmpdir) / "projects")
            manager.create_project(name="p1", path=Path(tmpdir) / "p1")
            manager.create_project(name="p2", path=Path(tmpdir) / "p2", template="api")
            
            stats = manager.get_stats()
            assert stats["total_projects"] == 2
            assert stats["active_projects"] == 2
            assert "web-app" in stats["by_template"]


class TestPluginManager:
    """Tests for PluginManager."""
    
    def test_init(self) -> None:
        """Test initialization."""
        manager = PluginManager()
        assert len(manager._plugins) == 0
    
    def test_list_plugins_empty(self) -> None:
        """Test listing with no plugins."""
        manager = PluginManager()
        plugins = manager.list_plugins()
        assert plugins == []
    
    def test_get_agents_empty(self) -> None:
        """Test getting agents with no plugins."""
        manager = PluginManager()
        agents = manager.get_agents()
        assert agents == []
    
    def test_get_tools_empty(self) -> None:
        """Test getting tools with no plugins."""
        manager = PluginManager()
        tools = manager.get_tools()
        assert tools == {}
    
    def test_register_hook(self) -> None:
        """Test hook registration."""
        manager = PluginManager()
        
        called = []
        def callback(data):
            called.append(data)
        
        manager.register_hook("test_event", callback)
        assert "test_event" in manager._hooks


class TestPluginMetadata:
    """Tests for PluginMetadata."""
    
    def test_create(self) -> None:
        """Test metadata creation."""
        metadata = PluginMetadata(
            name="test-plugin",
            version="1.0.0",
            description="A test plugin",
            author="Test Author",
        )
        
        assert metadata.name == "test-plugin"
        assert metadata.version == "1.0.0"


class TestCICDGenerator:
    """Tests for CICDGenerator."""
    
    def test_init(self) -> None:
        """Test initialization."""
        generator = CICDGenerator()
        assert "noode" in generator.templates
        assert "python" in generator.templates
    
    def test_generate_github_actions(self) -> None:
        """Test GitHub Actions generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = CICDGenerator()
            workflow_path = generator.generate_github_actions(
                Path(tmpdir),
                template="noode",
            )
            
            assert workflow_path.exists()
            content = workflow_path.read_text()
            assert "name: Noode CI" in content
            assert "Security Review" in content
    
    def test_generate_pre_commit(self) -> None:
        """Test pre-commit config generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = CICDGenerator()
            config_path = generator.generate_pre_commit(Path(tmpdir))
            
            assert config_path.exists()
            content = config_path.read_text()
            assert "noode-security" in content


class TestProjectConfig:
    """Tests for ProjectConfig."""
    
    def test_defaults(self) -> None:
        """Test default values."""
        config = ProjectConfig(name="test")
        
        assert config.name == "test"
        assert config.template == "web-app"
        assert config.version == "0.1.0"


class TestProject:
    """Tests for Project dataclass."""
    
    def test_to_dict(self) -> None:
        """Test serialization."""
        project = Project(
            project_id="abc123",
            name="test",
            path=Path("/tmp/test"),
            config=ProjectConfig(name="test"),
            created_at=datetime(2026, 1, 1),
            updated_at=datetime(2026, 1, 2),
        )
        
        data = project.to_dict()
        assert data["project_id"] == "abc123"
        assert data["name"] == "test"
    
    def test_from_dict(self) -> None:
        """Test deserialization."""
        data = {
            "project_id": "xyz",
            "name": "project",
            "path": "/tmp/project",
            "config": {
                "name": "project",
                "template": "api",
                "version": "1.0.0",
            },
            "created_at": "2026-01-01T00:00:00",
            "updated_at": "2026-01-02T00:00:00",
        }
        
        project = Project.from_dict(data)
        assert project.project_id == "xyz"
        assert project.config.template == "api"
