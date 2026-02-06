"""Pydantic models for API requests and responses."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: Literal["healthy", "unhealthy"] = "healthy"
    version: str = "0.5.0"
    timestamp: datetime = Field(default_factory=datetime.now)


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""
    
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=1000)
    template: str = Field(default="web-app")


class CreateProjectResponse(BaseModel):
    """Response after creating a project."""
    
    project_id: str
    name: str
    path: str
    status: str = "created"


class TaskRequest(BaseModel):
    """Request to execute a task."""
    
    task_type: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1, max_length=10000)
    project_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    """Response from task execution."""
    
    task_id: str
    status: Literal["pending", "running", "completed", "failed"]
    result: dict[str, Any] | None = None
    error: str | None = None
    duration_ms: float | None = None


class AgentStatus(BaseModel):
    """Status of an agent."""
    
    name: str
    role: str
    status: Literal["idle", "busy", "error"]
    capabilities: list[str]
    last_active: datetime | None = None


class ProjectInfo(BaseModel):
    """Project information."""
    
    project_id: str
    name: str
    template: str
    created_at: datetime
    updated_at: datetime
    is_active: bool


class ErrorResponse(BaseModel):
    """Error response."""
    
    error: str
    detail: str | None = None
    code: str = "UNKNOWN_ERROR"


# Knowledge Models
class Document(BaseModel):
    """A document in the knowledge store."""
    
    id: str | None = None
    content: str = Field(..., min_length=1)
    doc_type: Literal["text", "code", "markdown", "json"] = "text"
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class SearchRequest(BaseModel):
    """Request to search documents."""
    
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """A search result."""
    
    id: str
    content: str
    doc_type: str
    score: float
    metadata: dict[str, Any]


class KnowledgeStats(BaseModel):
    """Statistics about the knowledge store."""
    
    total_documents: int
    document_types: dict[str, int]
    storage_size_mb: float | None = None
