"""Research Agent for gathering information and best practices.

The Research Agent is responsible for:
- Searching current documentation and best practices
- Evaluating multiple approaches
- Synthesizing findings into recommendations
- Validating information from multiple sources
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx
import litellm
import structlog

from noode.core.base_agent import Action, BaseAgent, Result

logger = structlog.get_logger()


@dataclass
class ResearchFinding:
    """A finding from research."""
    
    source: str
    content: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    url: str | None = None
    verified: bool = False


@dataclass
class ResearchReport:
    """Complete research report."""
    
    query: str
    findings: list[ResearchFinding]
    recommendation: str
    confidence: float
    alternatives: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ResearchAgent(BaseAgent):
    """Agent specialized in research and information gathering.
    
    Conducts thorough investigation before implementation:
    - Searches documentation and community resources
    - Evaluates multiple approaches
    - Cross-references information
    - Synthesizes actionable recommendations
    """
    
    def __init__(
        self,
        name: str = "research_agent",
        model: str = "gpt-4o",
    ) -> None:
        """Initialize the research agent.
        
        Args:
            name: Agent name
            model: LLM model to use
        """
        super().__init__(
            name=name,
            role="Research and Information Specialist",
            capabilities=[
                "searching documentation",
                "evaluating best practices",
                "comparing approaches",
                "synthesizing recommendations",
                "validating information",
            ],
            model=model,
            confidence_threshold=0.7,
        )
        self._http_client = httpx.AsyncClient(timeout=30.0)
    
    async def act(self, action: Action) -> Result:
        """Execute a research action.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the research
        """
        start_time = datetime.now()
        
        try:
            if action.action_type == "research":
                report = await self.conduct_research(
                    query=action.parameters.get("query", ""),
                    context=action.parameters.get("context", {}),
                )
                return Result(
                    success=True,
                    output=report,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "validate":
                is_valid = await self.validate_approach(
                    approach=action.parameters.get("approach", ""),
                    requirements=action.parameters.get("requirements", []),
                )
                return Result(
                    success=True,
                    output={"valid": is_valid},
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            else:
                return Result(
                    success=False,
                    output=None,
                    error=f"Unknown action type: {action.action_type}",
                )
                
        except Exception as e:
            logger.error("research_action_failed", error=str(e))
            return Result(
                success=False,
                output=None,
                error=str(e),
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )
    
    async def conduct_research(
        self,
        query: str,
        context: dict[str, Any] | None = None,
    ) -> ResearchReport:
        """Conduct comprehensive research on a topic.
        
        Args:
            query: What to research
            context: Additional context (tech stack, requirements, etc.)
            
        Returns:
            Complete research report
        """
        logger.info("research_started", query=query[:100])
        
        context = context or {}
        findings: list[ResearchFinding] = []
        
        # Step 1: Generate search queries
        search_queries = await self._generate_search_queries(query, context)
        
        # Step 2: Search and gather information
        for sq in search_queries[:3]:  # Limit to top 3 queries
            finding = await self._search_and_analyze(sq)
            if finding:
                findings.append(finding)
        
        # Step 3: Synthesize findings into recommendation
        report = await self._synthesize_findings(query, findings, context)
        
        # Step 4: Identify alternatives and warnings
        report = await self._identify_alternatives(report)
        
        logger.info(
            "research_completed",
            query=query[:50],
            findings=len(findings),
            confidence=report.confidence,
        )
        
        return report
    
    async def validate_approach(
        self,
        approach: str,
        requirements: list[str],
    ) -> bool:
        """Validate an approach against requirements.
        
        Args:
            approach: The proposed approach
            requirements: List of requirements to check against
            
        Returns:
            True if approach is valid
        """
        thought = await self.think(
            f"""Validate this approach:
            
Approach: {approach}

Requirements:
{chr(10).join(f'- {r}' for r in requirements)}

Does the approach satisfy all requirements?
List any concerns or gaps."""
        )
        
        return thought.confidence >= self.confidence_threshold
    
    async def compare_approaches(
        self,
        approaches: list[str],
        criteria: list[str],
    ) -> dict[str, float]:
        """Compare multiple approaches.
        
        Args:
            approaches: List of approaches to compare
            criteria: Evaluation criteria
            
        Returns:
            Dict mapping approach to score (0-1)
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": self.system_prompt,
            }, {
                "role": "user",
                "content": f"""Compare these approaches:

Approaches:
{chr(10).join(f'{i+1}. {a}' for i, a in enumerate(approaches))}

Criteria:
{chr(10).join(f'- {c}' for c in criteria)}

Score each approach 0-1 on each criterion. Provide final weighted scores.""",
            }],
            temperature=0.3,
        )
        
        # Parse scores (simplified)
        content = response.choices[0].message.content or ""
        scores = {}
        
        for i, approach in enumerate(approaches):
            # Extract score for this approach
            import re
            pattern = rf"{i+1}.*?(\d+\.?\d*)"
            match = re.search(pattern, content)
            if match:
                score = float(match.group(1))
                scores[approach] = score if score <= 1 else score / 100
            else:
                scores[approach] = 0.5
        
        return scores
    
    async def _generate_search_queries(
        self,
        query: str,
        context: dict[str, Any],
    ) -> list[str]:
        """Generate effective search queries."""
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": "Generate search queries to research a technical topic effectively.",
            }, {
                "role": "user",
                "content": f"""Topic: {query}

Context:
- Tech stack: {context.get('tech_stack', 'not specified')}
- Version: {context.get('version', 'latest')}
- Requirements: {context.get('requirements', [])}

Generate 3 focused search queries. Include version numbers and year (2024-2026) for recency.""",
            }],
            temperature=0.5,
        )
        
        content = response.choices[0].message.content or query
        
        # Parse queries from response
        lines = [l.strip() for l in content.split("\n") if l.strip()]
        queries = [l.lstrip("0123456789.-) ") for l in lines if len(l) > 10]
        
        return queries[:3] if queries else [query]
    
    async def _search_and_analyze(self, query: str) -> ResearchFinding | None:
        """Search and analyze a single query."""
        # In production, this would use real search APIs
        # For now, we simulate with LLM knowledge
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": """You are a research assistant with up-to-date knowledge 
about software development best practices. Provide accurate, current information.""",
            }, {
                "role": "user",
                "content": f"Research query: {query}\n\nProvide current best practices and recommendations.",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        
        return ResearchFinding(
            source="llm_knowledge",
            content=content,
            confidence=0.7,  # Moderate confidence for LLM-only
            verified=False,
        )
    
    async def _synthesize_findings(
        self,
        query: str,
        findings: list[ResearchFinding],
        context: dict[str, Any],
    ) -> ResearchReport:
        """Synthesize findings into a report."""
        findings_text = "\n\n".join(
            f"Source: {f.source}\nConfidence: {f.confidence}\n{f.content}"
            for f in findings
        )
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": self.system_prompt,
            }, {
                "role": "user",
                "content": f"""Synthesize these research findings into a recommendation:

Query: {query}

Context: {context}

Findings:
{findings_text}

Provide:
1. Clear recommendation
2. Overall confidence (0-1)
3. Key considerations""",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        
        # Extract confidence
        confidence = self._extract_confidence(content)
        
        return ResearchReport(
            query=query,
            findings=findings,
            recommendation=content,
            confidence=confidence,
        )
    
    async def _identify_alternatives(self, report: ResearchReport) -> ResearchReport:
        """Identify alternatives and warnings."""
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": self.system_prompt,
            }, {
                "role": "user",
                "content": f"""For this recommendation:

{report.recommendation}

List:
1. Alternative approaches (if recommendation doesn't work)
2. Potential warnings or gotchas to watch for""",
            }],
            temperature=0.5,
        )
        
        content = response.choices[0].message.content or ""
        
        # Parse alternatives and warnings
        lines = content.split("\n")
        in_alternatives = False
        in_warnings = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "alternative" in line.lower():
                in_alternatives = True
                in_warnings = False
                continue
            elif "warning" in line.lower() or "gotcha" in line.lower():
                in_alternatives = False
                in_warnings = True
                continue
            
            if line.startswith(("-", "*", "•")) or line[0].isdigit():
                clean_line = line.lstrip("-*•0123456789.) ")
                if in_alternatives and clean_line:
                    report.alternatives.append(clean_line)
                elif in_warnings and clean_line:
                    report.warnings.append(clean_line)
        
        return report
    
    def _extract_confidence(self, content: str) -> float:
        """Extract confidence from response."""
        import re
        
        patterns = [
            r"confidence[:\s]+(\d+\.?\d*)",
            r"(\d+\.?\d*)\s*%",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content.lower())
            if match:
                value = float(match.group(1))
                return value / 100 if value > 1 else value
        
        return 0.6  # Default moderate confidence
    
    async def __aenter__(self) -> "ResearchAgent":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        """Async context manager exit."""
        await self._http_client.aclose()
