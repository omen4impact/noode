"""API routes for Noode."""

from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, status, Body
from pydantic import BaseModel, Field

from noode.api.models import (
    AgentStatus,
    CreateProjectRequest,
    CreateProjectResponse,
    Document,
    ErrorResponse,
    HealthResponse,
    KnowledgeStats,
    ProjectInfo,
    SearchRequest,
    SearchResult,
    TaskRequest,
    TaskResponse,
)

router = APIRouter()

# In-memory storage (would be replaced with proper database)
_projects: dict[str, Any] = {}
_tasks: dict[str, Any] = {}


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


@router.get("/agents", response_model=list[AgentStatus], tags=["Agents"])
async def list_agents() -> list[AgentStatus]:
    """List all available agents."""
    return [
        AgentStatus(
            name="requirements_agent",
            role="Requirements Analysis Specialist",
            status="idle",
            capabilities=[
                "analyzing requirements",
                "creating user stories",
                "defining acceptance criteria",
                "requirement prioritization",
            ],
        ),
        AgentStatus(
            name="research_agent",
            role="Research and Information Specialist",
            status="idle",
            capabilities=[
                "searching documentation",
                "evaluating best practices",
                "comparing approaches",
            ],
        ),
        AgentStatus(
            name="frontend_agent",
            role="Frontend Development and UI/UX Specialist",
            status="idle",
            capabilities=[
                "ui component generation",
                "responsive design",
                "accessibility compliance",
            ],
        ),
        AgentStatus(
            name="backend_agent",
            role="Backend Development and API Specialist",
            status="idle",
            capabilities=[
                "api design",
                "database schema design",
                "business logic",
                "authentication",
            ],
        ),
        AgentStatus(
            name="database_agent",
            role="Database Design and Optimization Specialist",
            status="idle",
            capabilities=[
                "schema design",
                "query optimization",
                "migration management",
                "data modeling",
            ],
        ),
        AgentStatus(
            name="security_agent",
            role="Security Analysis and Enforcement Specialist",
            status="idle",
            capabilities=[
                "vulnerability scanning",
                "dependency auditing",
                "security code review",
            ],
        ),
        AgentStatus(
            name="testing_agent",
            role="Testing and Quality Assurance Specialist",
            status="idle",
            capabilities=[
                "test generation",
                "test execution",
                "coverage analysis",
                "bug reporting",
            ],
        ),
    ]


@router.post(
    "/projects",
    response_model=CreateProjectResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Projects"],
)
async def create_project(request: CreateProjectRequest) -> CreateProjectResponse:
    """Create a new project."""
    import uuid
    
    project_id = str(uuid.uuid4())[:8]
    
    project = {
        "project_id": project_id,
        "name": request.name,
        "description": request.description,
        "template": request.template,
        "path": f"/projects/{request.name}",
    }
    
    _projects[project_id] = project
    
    return CreateProjectResponse(
        project_id=project_id,
        name=request.name,
        path=project["path"],
    )


@router.get("/projects", response_model=list[ProjectInfo], tags=["Projects"])
async def list_projects() -> list[ProjectInfo]:
    """List all projects."""
    from datetime import datetime
    
    return [
        ProjectInfo(
            project_id=p["project_id"],
            name=p["name"],
            template=p.get("template", "web-app"),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )
        for p in _projects.values()
    ]


@router.get("/projects/{project_id}", response_model=ProjectInfo, tags=["Projects"])
async def get_project(project_id: str) -> ProjectInfo:
    """Get project by ID."""
    from datetime import datetime
    
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    p = _projects[project_id]
    return ProjectInfo(
        project_id=p["project_id"],
        name=p["name"],
        template=p.get("template", "web-app"),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        is_active=True,
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Projects"])
async def delete_project(project_id: str) -> None:
    """Delete a project by ID."""
    if project_id not in _projects:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project {project_id} not found",
        )
    
    del _projects[project_id]
    return None


@router.post("/tasks", response_model=TaskResponse, tags=["Tasks"])
async def create_task(request: TaskRequest) -> TaskResponse:
    """Create and execute a task."""
    import uuid
    from datetime import datetime
    
    task_id = str(uuid.uuid4())[:8]
    
    task = {
        "task_id": task_id,
        "task_type": request.task_type,
        "description": request.description,
        "project_id": request.project_id,
        "parameters": request.parameters,
        "status": "pending",
        "created_at": datetime.now(),
    }
    
    _tasks[task_id] = task
    
    # TODO: Actually execute the task via orchestrator
    # For now, just return the task info
    
    return TaskResponse(
        task_id=task_id,
        status="pending",
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
async def get_task(task_id: str) -> TaskResponse:
    """Get task status and result."""
    if task_id not in _tasks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    
    task = _tasks[task_id]
    
    return TaskResponse(
        task_id=task_id,
        status=task.get("status", "pending"),
        result=task.get("result"),
        error=task.get("error"),
        duration_ms=task.get("duration_ms"),
    )


# Knowledge Endpoints
from noode.knowledge import KnowledgeStore

# Global knowledge store instance
_knowledge_store: KnowledgeStore | None = None


def get_knowledge_store() -> KnowledgeStore:
    """Get or create knowledge store instance."""
    global _knowledge_store
    if _knowledge_store is None:
        _knowledge_store = KnowledgeStore()
    return _knowledge_store


@router.post("/knowledge/documents", response_model=dict, status_code=status.HTTP_201_CREATED, tags=["Knowledge"])
async def add_document(document: Document) -> dict:
    """Add a document to the knowledge store."""
    from noode.knowledge.store import Document as KDocument
    
    try:
        store = get_knowledge_store()
        
        # Convert API model to internal Document
        kdoc = KDocument(
            content=document.content,
            doc_type=document.doc_type,
            metadata=document.metadata or {},
            doc_id=document.id,
        )
        
        doc_id = store.add_document(kdoc)
        
        return {"id": doc_id, "status": "created"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add document: {str(e)}",
        )


@router.post("/knowledge/search", response_model=list[SearchResult], tags=["Knowledge"])
async def search_documents(request: SearchRequest) -> list[SearchResult]:
    """Search documents in the knowledge store."""
    store = get_knowledge_store()
    
    results = store.search(request.query, top_k=request.top_k)
    
    return [
        SearchResult(
            id=doc.id,
            content=doc.content,
            doc_type=doc.doc_type,
            score=0.0,  # TODO: Add score from search results
            metadata=doc.metadata,
        )
        for doc in results
    ]


@router.delete("/knowledge/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Knowledge"])
async def delete_document(doc_id: str) -> None:
    """Delete a document from the knowledge store."""
    store = get_knowledge_store()
    
    deleted = store.delete_document(doc_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document {doc_id} not found",
        )
    
    return None


@router.get("/knowledge/stats", response_model=KnowledgeStats, tags=["Knowledge"])
async def get_knowledge_stats() -> KnowledgeStats:
    """Get statistics about the knowledge store."""
    store = get_knowledge_store()
    
    stats = store.get_stats()
    
    return KnowledgeStats(
        total_documents=stats.get("total_documents", 0),
        document_types=stats.get("document_types", {}),
        storage_size_mb=stats.get("storage_size_mb"),
    )


# Chat & LLM Endpoints
class ChatMessage(BaseModel):
    """A chat message."""
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    """Request to send chat message."""
    messages: List[ChatMessage] = Field(..., min_length=1)
    provider: Optional[str] = Field(default=None, description="LLM provider to use")
    model: Optional[str] = Field(default=None, description="Model to use")


class ChatResponse(BaseModel):
    """Response from chat."""
    content: str
    model: str
    provider: str
    error: Optional[str] = None


class ProviderStatus(BaseModel):
    """Status of an LLM provider."""
    name: str
    available: bool
    configured: bool


@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def chat(request: ChatRequest) -> ChatResponse:
    """Send chat message to LLM provider."""
    from noode.llm_providers import get_llm_manager, LLMMessage
    
    manager = get_llm_manager()
    
    # Convert to LLMMessage format
    messages = [
        LLMMessage(role=msg.role, content=msg.content)
        for msg in request.messages
    ]
    
    # Send to provider
    response = manager.chat(
        messages=messages,
        provider=request.provider,
        model=request.model,
    )
    
    return ChatResponse(
        content=response.content,
        model=response.model,
        provider=response.provider,
        error=response.error,
    )


@router.get("/chat/providers", response_model=List[ProviderStatus], tags=["Chat"])
async def get_providers() -> List[ProviderStatus]:
    """Get list of available LLM providers."""
    from noode.llm_providers import get_llm_manager
    
    manager = get_llm_manager()
    providers = []
    
    for name in ["openai", "anthropic", "google", "openrouter"]:
        provider = manager.providers.get(name)
        if provider:
            providers.append(ProviderStatus(
                name=name,
                available=provider.is_available(),
                configured=provider.config.get_api_key(name) is not None,
            ))
    
    return providers


@router.post("/chat/providers/{provider}/test", tags=["Chat"])
async def test_provider(provider: str) -> dict:
    """Test if a provider is working."""
    from noode.llm_providers import get_llm_manager
    
    manager = get_llm_manager()
    success = manager.test_provider(provider)
    
    return {
        "provider": provider,
        "success": success,
        "message": "Provider is working" if success else "Provider test failed",
    }


@router.post("/chat/providers/{provider}/key", tags=["Chat"])
async def set_provider_key(provider: str, api_key: str = Body(..., embed=True)) -> dict:
    """Set API key for a provider."""
    from noode.llm_providers import get_llm_manager
    
    manager = get_llm_manager()
    manager.config.set_api_key(provider, api_key)
    
    # Re-initialize provider
    if provider in manager.providers:
        if provider == "openai":
            from noode.llm_providers import OpenAIProvider
            manager.providers[provider] = OpenAIProvider(manager.config)
        elif provider == "anthropic":
            from noode.llm_providers import AnthropicProvider
            manager.providers[provider] = AnthropicProvider(manager.config)
        elif provider == "google":
            from noode.llm_providers import GoogleProvider
            manager.providers[provider] = GoogleProvider(manager.config)
        elif provider == "openrouter":
            from noode.llm_providers import OpenRouterProvider
            manager.providers[provider] = OpenRouterProvider(manager.config)
    
    return {
        "provider": provider,
        "status": "API key saved",
    }
