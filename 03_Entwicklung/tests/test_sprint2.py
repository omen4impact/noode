"""Tests for Sprint 2 components."""

import pytest
from pathlib import Path
import tempfile

from noode.nl_interface import (
    NaturalLanguageInterface,
    TaskIntent,
    ParsedTask,
)
from noode.project_generator import (
    ProjectGenerator,
    ProjectTemplate,
)


class TestNaturalLanguageInterface:
    """Tests for NL Interface."""
    
    def test_init(self) -> None:
        """Test NL interface initialization."""
        nl = NaturalLanguageInterface()
        assert nl.model == "gpt-4o"
        assert nl.conversation.messages == []
    
    def test_intent_keywords_create_project(self) -> None:
        """Test intent detection for project creation."""
        nl = NaturalLanguageInterface()
        intent = nl._detect_intent_keywords("Erstelle ein neues Projekt")
        assert intent == TaskIntent.CREATE_PROJECT
    
    def test_intent_keywords_ui(self) -> None:
        """Test intent detection for UI tasks."""
        nl = NaturalLanguageInterface()
        intent = nl._detect_intent_keywords("Erstelle eine Login-Seite")
        assert intent == TaskIntent.GENERATE_UI
    
    def test_intent_keywords_api(self) -> None:
        """Test intent detection for API tasks."""
        nl = NaturalLanguageInterface()
        intent = nl._detect_intent_keywords("Erstelle einen REST API endpoint")
        assert intent == TaskIntent.GENERATE_API
    
    def test_intent_keywords_security(self) -> None:
        """Test intent detection for security tasks."""
        nl = NaturalLanguageInterface()
        intent = nl._detect_intent_keywords("Prüfe den Code auf Sicherheitslücken")
        assert intent == TaskIntent.SECURITY_REVIEW
    
    def test_intent_keywords_unknown(self) -> None:
        """Test fallback for unknown intent."""
        nl = NaturalLanguageInterface()
        intent = nl._detect_intent_keywords("xyz abc 123")
        assert intent == TaskIntent.UNKNOWN
    
    def test_suggest_agents_ui(self) -> None:
        """Test agent suggestions for UI intent."""
        nl = NaturalLanguageInterface()
        agents = nl._suggest_agents(TaskIntent.GENERATE_UI)
        assert "frontend" in agents
    
    def test_suggest_agents_api(self) -> None:
        """Test agent suggestions for API intent."""
        nl = NaturalLanguageInterface()
        agents = nl._suggest_agents(TaskIntent.GENERATE_API)
        assert "backend" in agents
        assert "security" in agents
    
    def test_set_context(self) -> None:
        """Test setting conversation context."""
        nl = NaturalLanguageInterface()
        nl.set_context(project="myproject", file="main.py")
        assert nl.conversation.current_project == "myproject"
        assert nl.conversation.current_file == "main.py"
    
    def test_clear_context(self) -> None:
        """Test clearing conversation context."""
        nl = NaturalLanguageInterface()
        nl.set_context(project="myproject")
        nl.clear_context()
        assert nl.conversation.current_project is None


class TestProjectGenerator:
    """Tests for Project Generator."""
    
    def test_list_templates(self) -> None:
        """Test listing available templates."""
        templates = ProjectGenerator.list_templates()
        assert len(templates) >= 3
        
        template_ids = [t["id"] for t in templates]
        assert "web-app" in template_ids
        assert "api" in template_ids
    
    def test_generate_api_project(self) -> None:
        """Test generating API project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(Path(tmpdir))
            files = generator.generate(
                ProjectTemplate.API,
                "test_api",
            )
            
            assert len(files) > 0
            
            # Check project structure
            project_path = Path(tmpdir) / "test_api"
            assert project_path.exists()
            assert (project_path / "noode.yaml").exists()
            assert (project_path / "app" / "main.py").exists()
    
    def test_generate_creates_vmodel_structure(self) -> None:
        """Test that V-Model structure is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(Path(tmpdir))
            generator.generate(ProjectTemplate.API, "test_vmodel")
            
            project_path = Path(tmpdir) / "test_vmodel"
            assert (project_path / "00_Projektmanagement").exists()
            assert (project_path / "01_Anforderungen").exists()
            assert (project_path / ".noode").exists()
    
    def test_noode_config_content(self) -> None:
        """Test that noode.yaml has correct content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = ProjectGenerator(Path(tmpdir))
            generator.generate(ProjectTemplate.API, "config_test")
            
            config_path = Path(tmpdir) / "config_test" / "noode.yaml"
            content = config_path.read_text()
            
            assert "project:" in content
            assert "config_test" in content
            assert "agents:" in content
