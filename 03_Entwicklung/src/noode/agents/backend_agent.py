"""Backend Agent for API and business logic development.

The Backend Agent is responsible for:
- Designing and implementing RESTful APIs
- Database schema design and migrations
- Business logic implementation
- Integration with external services
- Performance optimization
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import litellm
import structlog

from noode.core.base_agent import Action, BaseAgent, Result
from noode.utils.validation import sanitize_for_prompt

logger = structlog.get_logger()


class DatabaseType(Enum):
    """Supported database types."""
    
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLITE = "sqlite"
    MONGODB = "mongodb"
    REDIS = "redis"


class APIStyle(Enum):
    """API design styles."""
    
    REST = "rest"
    GRAPHQL = "graphql"
    GRPC = "grpc"


class HTTPMethod(Enum):
    """HTTP methods."""
    
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


@dataclass
class Endpoint:
    """An API endpoint definition."""
    
    path: str
    method: HTTPMethod
    description: str
    request_body: dict[str, Any] | None = None
    response_schema: dict[str, Any] = field(default_factory=dict)
    path_params: list[str] = field(default_factory=list)
    query_params: list[str] = field(default_factory=list)
    auth_required: bool = True
    rate_limit: str | None = None


@dataclass
class DatabaseModel:
    """A database model definition."""
    
    name: str
    table_name: str
    fields: dict[str, str]
    primary_key: str = "id"
    indexes: list[str] = field(default_factory=list)
    relationships: dict[str, str] = field(default_factory=dict)


@dataclass
class APISpec:
    """Complete API specification."""
    
    name: str
    version: str
    base_path: str
    endpoints: list[Endpoint]
    models: list[DatabaseModel]
    auth_scheme: str = "jwt"


class BackendAgent(BaseAgent):
    """Agent specialized in backend development.
    
    Creates robust, scalable backend APIs and business logic
    following best practices for security and performance.
    """
    
    def __init__(
        self,
        name: str = "backend_agent",
        model: str = "gpt-4o",
        api_style: APIStyle = APIStyle.REST,
        database: DatabaseType = DatabaseType.POSTGRESQL,
    ) -> None:
        """Initialize the backend agent.
        
        Args:
            name: Agent name
            model: LLM model to use
            api_style: Preferred API style
            database: Database type to use
        """
        super().__init__(
            name=name,
            role="Backend Development and API Specialist",
            capabilities=[
                "api design",
                "database schema design",
                "business logic",
                "authentication",
                "caching",
                "performance optimization",
            ],
            model=model,
            confidence_threshold=0.8,
        )
        self.api_style = api_style
        self.database = database
    
    async def act(self, action: Action) -> Result:
        """Execute a backend action.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the backend generation
        """
        start_time = datetime.now()
        
        try:
            if action.action_type == "design_api":
                spec = await self.design_api(
                    description=action.parameters.get("description", ""),
                    resources=action.parameters.get("resources", []),
                )
                return Result(
                    success=True,
                    output=spec,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "generate_endpoint":
                code = await self.generate_endpoint(
                    endpoint=Endpoint(**action.parameters.get("endpoint", {})),
                    framework=action.parameters.get("framework", "fastapi"),
                )
                return Result(
                    success=True,
                    output=code,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "design_schema":
                models = await self.design_schema(
                    description=action.parameters.get("description", ""),
                    entities=action.parameters.get("entities", []),
                )
                return Result(
                    success=True,
                    output=models,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "generate_migration":
                migration = await self.generate_migration(
                    model=DatabaseModel(**action.parameters.get("model", {})),
                )
                return Result(
                    success=True,
                    output=migration,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            else:
                return Result(
                    success=False,
                    output=None,
                    error=f"Unknown action type: {action.action_type}",
                )
                
        except Exception as e:
            logger.error("backend_action_failed", error=str(e))
            return Result(
                success=False,
                output=None,
                error=str(e),
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )
    
    async def design_api(
        self,
        description: str,
        resources: list[str],
    ) -> APISpec:
        """Design a complete API from description.
        
        Args:
            description: What the API should do
            resources: List of resources/entities
            
        Returns:
            Complete API specification
        """
        logger.info("designing_api", description=description[:50])
        
        # Sanitize inputs for prompt injection protection
        safe_description = sanitize_for_prompt(description)
        safe_resources = sanitize_for_prompt(str(resources))
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"""{self.system_prompt}

You are designing a {self.api_style.value.upper()} API.
Follow these principles:
- RESTful resource naming (plural nouns)
- Proper HTTP status codes
- Consistent error handling
- Pagination for list endpoints
- Rate limiting consideration
- JWT authentication by default
- OpenAPI 3.0 compatible""",
            }, {
                "role": "user",
                "content": f"""Design an API for:

{safe_description}

Resources: {safe_resources}

Provide a complete API specification with:
1. All endpoints (CRUD + custom actions)
2. Request/response schemas
3. Authentication requirements
4. Rate limits if applicable""",
            }],
            temperature=0.5,
        )
        
        content = response.choices[0].message.content or ""
        
        # Parse API spec from response
        endpoints = self._parse_endpoints(content)
        
        return APISpec(
            name=self._generate_api_name(description),
            version="1.0.0",
            base_path="/api/v1",
            endpoints=endpoints,
            models=[],
            auth_scheme="jwt",
        )
    
    async def generate_endpoint(
        self,
        endpoint: Endpoint,
        framework: str = "fastapi",
    ) -> str:
        """Generate code for an endpoint.
        
        Args:
            endpoint: Endpoint specification
            framework: Backend framework
            
        Returns:
            Generated endpoint code
        """
        logger.info("generating_endpoint", path=endpoint.path, method=endpoint.method.value)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"""{self.system_prompt}

Generate production-ready {framework} code with:
- Type hints and validation
- Proper error handling
- Logging
- Security best practices
- Documentation strings""",
            }, {
                "role": "user",
                "content": f"""Generate {framework} code for this endpoint:

Path: {endpoint.path}
Method: {endpoint.method.value.upper()}
Description: {endpoint.description}
Auth required: {endpoint.auth_required}
Request body: {endpoint.request_body}
Response: {endpoint.response_schema}

Include:
1. Route decorator
2. Request model (if POST/PUT/PATCH)
3. Response model
4. Handler function with business logic
5. Error handling""",
            }],
            temperature=0.4,
        )
        
        content = response.choices[0].message.content or ""
        
        # Extract code block
        return self._extract_code(content, "python")
    
    async def design_schema(
        self,
        description: str,
        entities: list[str],
    ) -> list[DatabaseModel]:
        """Design database schema.
        
        Args:
            description: What the data should represent
            entities: List of entity names
            
        Returns:
            List of database models
        """
        logger.info("designing_schema", entities=entities)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"""{self.system_prompt}

Design a {self.database.value} schema with:
- Proper normalization (3NF)
- Appropriate indexes
- Foreign key relationships
- Type safety
- Created/updated timestamps
- Soft delete support""",
            }, {
                "role": "user",
                "content": f"""Design database schema for:

{description}

Entities: {entities}

For each entity, provide:
1. Table name
2. All fields with types
3. Primary key
4. Indexes
5. Relationships to other tables""",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        
        return self._parse_models(content, entities)
    
    async def generate_migration(
        self,
        model: DatabaseModel,
    ) -> str:
        """Generate database migration for a model.
        
        Args:
            model: Database model to create migration for
            
        Returns:
            Migration SQL or ORM code
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"Generate {self.database.value} migration code.",
            }, {
                "role": "user",
                "content": f"""Generate migration for this model:

Table: {model.table_name}
Fields: {model.fields}
Primary key: {model.primary_key}
Indexes: {model.indexes}
Relationships: {model.relationships}

Use alembic/SQLAlchemy format.""",
            }],
            temperature=0.2,
        )
        
        content = response.choices[0].message.content or ""
        return self._extract_code(content, "python")
    
    async def generate_crud_service(
        self,
        model: DatabaseModel,
    ) -> str:
        """Generate CRUD service for a model.
        
        Args:
            model: Database model
            
        Returns:
            Service class code
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"""{self.system_prompt}

Generate a service layer with:
- Async database operations
- Transaction handling
- Error handling
- Logging
- Type hints""",
            }, {
                "role": "user",
                "content": f"""Generate CRUD service for:

Model: {model.name}
Table: {model.table_name}
Fields: {model.fields}

Include:
- create(), get_by_id(), list(), update(), delete()
- Pagination support
- Filtering support
- Soft delete""",
            }],
            temperature=0.4,
        )
        
        content = response.choices[0].message.content or ""
        return self._extract_code(content, "python")
    
    def _parse_endpoints(self, content: str) -> list[Endpoint]:
        """Parse endpoints from LLM response."""
        endpoints = []
        
        # Simple parsing - look for HTTP methods and paths
        import re
        
        patterns = [
            (HTTPMethod.GET, r"GET\s+(/\S+)"),
            (HTTPMethod.POST, r"POST\s+(/\S+)"),
            (HTTPMethod.PUT, r"PUT\s+(/\S+)"),
            (HTTPMethod.PATCH, r"PATCH\s+(/\S+)"),
            (HTTPMethod.DELETE, r"DELETE\s+(/\S+)"),
        ]
        
        for method, pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for path in matches:
                endpoints.append(Endpoint(
                    path=path,
                    method=method,
                    description=f"{method.value.upper()} {path}",
                ))
        
        return endpoints
    
    def _parse_models(
        self,
        content: str,
        entities: list[str],
    ) -> list[DatabaseModel]:
        """Parse database models from LLM response."""
        models = []
        
        for entity in entities:
            # Create basic model structure
            model = DatabaseModel(
                name=entity.title().replace(" ", ""),
                table_name=entity.lower().replace(" ", "_") + "s",
                fields={
                    "id": "UUID PRIMARY KEY",
                    "created_at": "TIMESTAMP",
                    "updated_at": "TIMESTAMP",
                    "deleted_at": "TIMESTAMP NULL",
                },
                indexes=["created_at"],
            )
            models.append(model)
        
        return models
    
    def _extract_code(self, content: str, language: str) -> str:
        """Extract code block from response."""
        import re
        
        pattern = rf"```{language}\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            return match.group(1).strip()
        
        # Try without language specifier
        pattern = r"```\n(.*?)```"
        match = re.search(pattern, content, re.DOTALL)
        
        return match.group(1).strip() if match else content
    
    def _generate_api_name(self, description: str) -> str:
        """Generate API name from description."""
        words = description.split()[:2]
        return "_".join(w.lower() for w in words if w.isalnum()) + "_api"
