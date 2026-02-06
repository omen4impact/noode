"""Database Agent for database schema design and query generation.

This agent specializes in:
- Database schema design
- SQL query generation
- Data modeling
- Migration scripts
- Query optimization suggestions
"""

import structlog
from typing import Optional

import litellm

from noode.core.base_agent import Action, BaseAgent, Result
from noode.utils.validation import sanitize_for_prompt

logger = structlog.get_logger()


class DatabaseAgent(BaseAgent):
    """Agent for database design and management."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        confidence_threshold: float = 0.7,
    ):
        super().__init__(
            name="database_agent",
            role="Database Design and Management Specialist",
            capabilities=[
                "design_schema",
                "generate_queries",
                "optimize_database",
            ],
            model=model,
            api_key=api_key,
            confidence_threshold=confidence_threshold,
        )
        
        self.system_prompt = """You are a Database Design Specialist.

Your role is to:
1. Design efficient database schemas
2. Generate SQL queries and migrations
3. Model data relationships
4. Optimize database performance
5. Ensure data integrity and normalization

Expertise:
- Relational databases (PostgreSQL, MySQL, SQLite)
- NoSQL databases (MongoDB, Redis)
- Data modeling and normalization
- Indexing strategies
- Query optimization
- Migration scripts

Always:
- Follow database best practices
- Consider scalability and performance
- Ensure data integrity with constraints
- Provide both SQL DDL and DML
- Include indexing recommendations
- Think about migration paths"""
    
    async def think(self, context: str) -> dict:
        """Analyze database requirements."""
        logger.info("analyzing_database_requirements", context_length=len(context))
        
        safe_context = sanitize_for_prompt(context)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""Analyze the following requirements and suggest a database approach:

{safe_context}

Please provide:
1. Recommended database type (SQL vs NoSQL)
2. Main entities and relationships
3. Key tables/collections
4. Important considerations
5. Scalability approach

Keep it high-level and strategic."""
                }
            ],
            temperature=0.3,
        )
        
        analysis = response.choices[0].message.content
        
        return {
            "analysis": analysis,
            "confidence": 0.9,
            "requires_review": False,
        }
    
    async def act(self, action: Action) -> Result:
        """Execute database-related actions."""
        if action.type == "design_schema":
            return await self._design_schema(action.payload)
        elif action.type == "generate_queries":
            return await self._generate_queries(action.payload)
        elif action.type == "create_migrations":
            return await self._create_migrations(action.payload)
        elif action.type == "optimize_schema":
            return await self._optimize_schema(action.payload)
        else:
            return Result(
                success=False,
                data={},
                error=f"Unknown action type: {action.type}",
            )
    
    async def _design_schema(self, payload: dict) -> Result:
        """Design database schema from requirements."""
        try:
            requirements = payload.get("requirements", "")
            tech_stack = payload.get("tech_stack", "PostgreSQL")
            
            safe_requirements = sanitize_for_prompt(requirements)
            
            logger.info("designing_schema", tech_stack=tech_stack)
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Design a complete database schema for:

Requirements:
{safe_requirements}

Technology: {tech_stack}

Provide:

## 1. Entity-Relationship Diagram (Text-based)
Describe entities and their relationships

## 2. Complete SQL Schema (DDL)
```sql
-- Create tables with:
-- - Primary keys
-- - Foreign keys
-- - Constraints (NOT NULL, UNIQUE, CHECK)
-- - Indexes
-- - Comments
```

## 3. Data Types & Constraints
Explain choices for:
- Primary key strategies
- Data type selections
- Constraint decisions

## 4. Indexes
List recommended indexes with rationale

## 5. Normalization
Explain normalization level (3NF, etc.)

## 6. Relationships
Detail all foreign key relationships

## 7. Sample Data (Optional)
Insert statements for testing

Ensure the schema is production-ready with proper constraints and indexing."""
                    }
                ],
                temperature=0.3,
            )
            
            schema = response.choices[0].message.content
            
            # Extract SQL code blocks
            sql_statements = self._extract_sql(schema)
            
            return Result(
                success=True,
                data={
                    "schema_design": schema,
                    "sql_statements": sql_statements,
                    "database_type": tech_stack,
                },
            )
            
        except Exception as e:
            logger.error("schema_design_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _generate_queries(self, payload: dict) -> Result:
        """Generate SQL queries for common operations."""
        try:
            schema = payload.get("schema", "")
            operations = payload.get("operations", ["CRUD"])
            
            safe_schema = sanitize_for_prompt(schema)
            
            logger.info("generating_queries", operations=operations)
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Generate SQL queries for the following schema:

{safe_schema}

Generate queries for these operations:
{', '.join(operations)}

Include:

## 1. SELECT Queries
- Basic SELECT with filters
- JOIN queries
- Aggregation queries (GROUP BY, COUNT, SUM, etc.)
- Pagination queries (LIMIT/OFFSET or equivalent)
- Search queries with LIKE/Full-text

## 2. INSERT Queries
- Single row insert
- Batch insert
- Insert with RETURNING clause

## 3. UPDATE Queries
- Update with conditions
- Update with JOINs (if applicable)
- Upsert/ON CONFLICT

## 4. DELETE Queries
- Soft delete (if applicable)
- Hard delete with constraints
- Cascading deletes

## 5. Advanced Queries
- Common Table Expressions (CTEs)
- Window functions (if useful)
- Stored procedures (if applicable)

Format all queries with proper indentation and comments."""
                    }
                ],
                temperature=0.3,
            )
            
            queries = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"queries": queries},
            )
            
        except Exception as e:
            logger.error("query_generation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _create_migrations(self, payload: dict) -> Result:
        """Create database migration scripts."""
        try:
            current_schema = payload.get("current_schema", "")
            target_schema = payload.get("target_schema", "")
            migration_tool = payload.get("migration_tool", "alembic")
            
            safe_current = sanitize_for_prompt(current_schema)
            safe_target = sanitize_for_prompt(target_schema)
            
            logger.info("creating_migrations", tool=migration_tool)
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Create migration scripts from current to target schema.

Migration Tool: {migration_tool}

Current Schema:
{safe_current}

Target Schema:
{safe_target}

Provide:

## 1. Migration Steps
List all changes needed (add tables, columns, indexes, etc.)

## 2. Migration Script
```sql
-- Forward migration (upgrade)
-- Include all ALTER TABLE, CREATE statements
-- Add safety checks (IF NOT EXISTS)
-- Include transaction blocks
```

## 3. Rollback Script
```sql
-- Backward migration (downgrade)
-- Reverse all changes
-- Safe rollback procedures
```

## 4. Data Migration (if needed)
- Transform existing data
- Default values
- Data validation

## 5. Verification Queries
- Queries to verify migration success
- Integrity checks

Ensure migrations are safe and reversible."""
                    }
                ],
                temperature=0.3,
            )
            
            migrations = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"migrations": migrations},
            )
            
        except Exception as e:
            logger.error("migration_creation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _optimize_schema(self, payload: dict) -> Result:
        """Suggest schema optimizations."""
        try:
            current_schema = payload.get("schema", "")
            performance_issues = payload.get("performance_issues", [])
            
            safe_schema = sanitize_for_prompt(current_schema)
            
            logger.info("optimizing_schema")
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Analyze and optimize this database schema:

Current Schema:
{safe_schema}

Known Issues:
{chr(10).join(f"- {issue}" for issue in performance_issues) if performance_issues else "None reported"}

Provide optimization recommendations:

## 1. Indexing Strategy
- Missing indexes
- Composite indexes
- Covering indexes
- Index maintenance

## 2. Query Optimization
- Slow query patterns to avoid
- Query refactoring suggestions
- EXPLAIN plan considerations

## 3. Schema Refactoring
- Denormalization opportunities (if beneficial)
- Partitioning strategies
- Archiving old data

## 4. Connection Pooling
- Recommended pool sizes
- Connection management

## 5. Caching Strategy
- Query result caching
- Materialized views

## 6. Monitoring
- Key metrics to track
- Alerting thresholds"""
                    }
                ],
                temperature=0.3,
            )
            
            optimizations = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"optimizations": optimizations},
            )
            
        except Exception as e:
            logger.error("optimization_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    def _extract_sql(self, text: str) -> list[str]:
        """Extract SQL statements from markdown text."""
        import re
        
        # Find SQL code blocks
        sql_blocks = re.findall(r'```sql\n(.*?)\n```', text, re.DOTALL)
        
        statements = []
        for block in sql_blocks:
            # Split by semicolon to get individual statements
            for stmt in block.split(';'):
                stmt = stmt.strip()
                if stmt and not stmt.startswith('--') and not stmt.startswith('/*'):
                    statements.append(stmt + ';')
        
        return statements
    
    async def review_output(self, output: dict, reviewer: str = "") -> dict:
        """Review database designs."""
        review_prompt = f"""Review this database schema for:
1. Normalization (proper 3NF)
2. Indexing strategy
3. Data integrity (constraints)
4. Scalability considerations
5. Security (injection prevention)

Schema to review:
{output.get('schema_design', '')}

Provide approval status and any concerns."""
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior DBA reviewing database designs."},
                {"role": "user", "content": review_prompt}
            ],
            temperature=0.3,
        )
        
        review_text = response.choices[0].message.content
        approved = "approved" in review_text.lower() or "approve" in review_text.lower()
        
        return {
            "approved": approved,
            "review_comments": review_text,
            "suggested_changes": [] if approved else [review_text],
        }
