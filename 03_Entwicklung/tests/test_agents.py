"""Tests for Sprint 1 agents."""

import pytest

from noode.agents.security_agent import (
    SecurityAgent,
    SecurityFinding,
    Severity,
    VulnerabilityType,
)
from noode.agents.frontend_agent import (
    FrontendAgent,
    UIFramework,
    ComponentType,
)
from noode.agents.backend_agent import (
    BackendAgent,
    APIStyle,
    DatabaseType,
    HTTPMethod,
)
from noode.core.knowledge_store import KnowledgeStore, KnowledgeEntry


class TestSecurityAgent:
    """Tests for SecurityAgent."""
    
    def test_init(self) -> None:
        """Test security agent initialization."""
        agent = SecurityAgent()
        assert agent.name == "security_agent"
        assert agent.confidence_threshold == 0.9
        assert "vulnerability scanning" in agent.capabilities
    
    def test_severity_mapping(self) -> None:
        """Test vulnerability severity mapping."""
        agent = SecurityAgent()
        assert agent._get_severity(VulnerabilityType.SQL_INJECTION) == Severity.CRITICAL
        assert agent._get_severity(VulnerabilityType.XSS) == Severity.HIGH
        assert agent._get_severity(VulnerabilityType.CSRF) == Severity.MEDIUM
    
    def test_risk_score_calculation(self) -> None:
        """Test risk score calculation."""
        agent = SecurityAgent()
        
        # No findings = 0 risk
        assert agent._calculate_risk_score([]) == 0.0
        
        # Critical finding = high risk
        findings = [SecurityFinding(
            finding_id="test",
            vulnerability_type=VulnerabilityType.SQL_INJECTION,
            severity=Severity.CRITICAL,
            title="SQL Injection",
            description="Test",
            location="test.py:1",
            recommendation="Fix it",
        )]
        assert agent._calculate_risk_score(findings) == 3.0


class TestFrontendAgent:
    """Tests for FrontendAgent."""
    
    def test_init(self) -> None:
        """Test frontend agent initialization."""
        agent = FrontendAgent()
        assert agent.name == "frontend_agent"
        assert agent.framework == UIFramework.REACT
        assert "ui component generation" in agent.capabilities
    
    def test_default_design_tokens(self) -> None:
        """Test default design tokens are set."""
        agent = FrontendAgent()
        assert "primary" in agent.design_tokens["colors"]
        assert agent.design_tokens["colors"]["primary"] == "#6366f1"
    
    def test_component_name_generation(self) -> None:
        """Test component name generation."""
        agent = FrontendAgent()
        name = agent._generate_component_name("User profile card with avatar")
        assert name == "UserProfileCard"
    
    def test_base_styles_generation(self) -> None:
        """Test base styles generation."""
        agent = FrontendAgent()
        styles = agent._generate_base_styles()
        assert "--color-primary" in styles
        assert "font-family" in styles


class TestBackendAgent:
    """Tests for BackendAgent."""
    
    def test_init(self) -> None:
        """Test backend agent initialization."""
        agent = BackendAgent()
        assert agent.name == "backend_agent"
        assert agent.api_style == APIStyle.REST
        assert agent.database == DatabaseType.POSTGRESQL
    
    def test_api_name_generation(self) -> None:
        """Test API name generation."""
        agent = BackendAgent()
        name = agent._generate_api_name("User management system")
        assert name == "user_management_api"


class TestKnowledgeStore:
    """Tests for KnowledgeStore."""
    
    def test_init(self) -> None:
        """Test knowledge store initialization."""
        store = KnowledgeStore()
        assert store.storage_path is None
        assert len(store._entries) == 0
    
    def test_get_stats_empty(self) -> None:
        """Test stats for empty store."""
        store = KnowledgeStore()
        stats = store.get_stats()
        assert stats["total_entries"] == 0
        assert stats["storage_path"] == "memory"
    
    def test_cosine_similarity(self) -> None:
        """Test cosine similarity calculation."""
        store = KnowledgeStore()
        
        # Same vector = 1.0
        vec = [1.0, 0.0, 0.0]
        assert store._cosine_similarity(vec, vec) == 1.0
        
        # Orthogonal = 0.0
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        assert store._cosine_similarity(vec1, vec2) == 0.0
