"""Requirements Agent for analyzing and structuring project requirements.

This agent specializes in:
- Analyzing user descriptions and extracting requirements
- Creating structured requirement documents
- Generating user stories and acceptance criteria
- Identifying functional and non-functional requirements
"""

import structlog
from typing import Optional

import litellm

from noode.core.base_agent import Action, BaseAgent, Result
from noode.utils.validation import sanitize_for_prompt

logger = structlog.get_logger()


class RequirementsAgent(BaseAgent):
    """Agent for requirements analysis and documentation."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        confidence_threshold: float = 0.7,
    ):
        super().__init__(
            name="requirements_agent",
            role="Requirements Analysis and Documentation Specialist",
            capabilities=[
                "analyze_requirements",
                "generate_user_stories",
                "create_specifications",
            ],
            model=model,
            api_key=api_key,
            confidence_threshold=confidence_threshold,
        )
        
        self.system_prompt = """You are a Requirements Analysis Specialist.

Your role is to:
1. Analyze user descriptions and extract clear, structured requirements
2. Distinguish between functional and non-functional requirements
3. Create user stories with acceptance criteria
4. Identify edge cases and constraints
5. Generate technical specifications

Always:
- Be precise and unambiguous
- Use standard requirement formats
- Consider both happy path and edge cases
- Think about security, performance, and scalability
- Ask clarifying questions when requirements are unclear

Output should be structured, actionable, and ready for implementation."""
    
    async def think(self, context: str) -> dict:
        """Analyze requirements from context."""
        logger.info("analyzing_requirements", context_length=len(context))
        
        safe_context = sanitize_for_prompt(context)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""Analyze the following project description and extract structured requirements:

{safe_context}

Please provide:
1. Project Overview (2-3 sentences)
2. Functional Requirements (bullet points)
3. Non-Functional Requirements (performance, security, scalability)
4. User Stories (As a [user], I want [goal], so that [benefit])
5. Acceptance Criteria for each user story
6. Edge Cases to consider
7. Technical Constraints
8. Open Questions (if any)

Format your response as a structured markdown document."""
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
        """Execute requirements-related actions."""
        if action.type == "analyze_requirements":
            return await self._analyze_requirements(action.payload)
        elif action.type == "generate_user_stories":
            return await self._generate_user_stories(action.payload)
        elif action.type == "create_specifications":
            return await self._create_specifications(action.payload)
        else:
            return Result(
                success=False,
                data={},
                error=f"Unknown action type: {action.type}",
            )
    
    async def _analyze_requirements(self, payload: dict) -> Result:
        """Analyze and structure requirements from description."""
        try:
            description = payload.get("description", "")
            safe_description = sanitize_for_prompt(description)
            
            logger.info("analyzing_requirements", description_length=len(description))
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Analyze this project description:

{safe_description}

Provide a comprehensive requirements analysis including:

## 1. Executive Summary
Brief overview of what needs to be built

## 2. Functional Requirements
- Core features
- User interactions
- Data processing needs
- Integration points

## 3. Non-Functional Requirements
- Performance expectations
- Security requirements
- Scalability needs
- Reliability/availability
- Compliance requirements

## 4. User Stories
Format: As a [type of user], I want [some goal], so that [some reason]
Include acceptance criteria for each

## 5. Constraints & Assumptions
- Technical constraints
- Business constraints
- Assumptions made

## 6. Open Questions
What needs clarification?"""
                    }
                ],
                temperature=0.3,
            )
            
            analysis = response.choices[0].message.content
            
            return Result(
                success=True,
                data={
                    "requirements_analysis": analysis,
                    "project_type": self._detect_project_type(description),
                },
            )
            
        except Exception as e:
            logger.error("requirements_analysis_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _generate_user_stories(self, payload: dict) -> Result:
        """Generate user stories from requirements."""
        try:
            requirements = payload.get("requirements", "")
            safe_requirements = sanitize_for_prompt(requirements)
            
            logger.info("generating_user_stories")
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Generate detailed user stories from these requirements:

{safe_requirements}

For each user story, provide:
- Story ID (e.g., US-001)
- User Story (As a..., I want..., so that...)
- Acceptance Criteria (Given/When/Then format)
- Priority (Must/Should/Could/Won't)
- Story Points estimate (1, 2, 3, 5, 8, 13)
- Dependencies (if any)

Also identify:
- MVP features (minimum viable product)
- Phase 2 features
- Technical debt items"""
                    }
                ],
                temperature=0.3,
            )
            
            stories = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"user_stories": stories},
            )
            
        except Exception as e:
            logger.error("user_stories_generation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _create_specifications(self, payload: dict) -> Result:
        """Create technical specifications."""
        try:
            requirements = payload.get("requirements", "")
            user_stories = payload.get("user_stories", "")
            
            safe_requirements = sanitize_for_prompt(requirements)
            safe_stories = sanitize_for_prompt(user_stories)
            
            logger.info("creating_specifications")
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Create technical specifications based on:

Requirements:
{safe_requirements}

User Stories:
{safe_stories}

Provide:

## 1. System Architecture Overview
- High-level architecture
- Main components
- Data flow

## 2. API Specifications
- Endpoints needed
- Request/response formats
- Authentication requirements

## 3. Data Model
- Entities
- Relationships
- Database schema suggestions

## 4. UI/UX Specifications
- Key screens
- User flows
- Responsive design requirements

## 5. Integration Points
- External services
- APIs to consume
- Third-party libraries

## 6. Technical Stack Recommendations
- Frontend framework
- Backend technology
- Database
- Deployment strategy"""
                    }
                ],
                temperature=0.3,
            )
            
            specs = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"technical_specifications": specs},
            )
            
        except Exception as e:
            logger.error("specifications_creation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    def _detect_project_type(self, description: str) -> str:
        """Detect the type of project from description."""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ["web", "website", "webapp", "web app"]):
            return "web_application"
        elif any(word in desc_lower for word in ["mobile", "app", "ios", "android"]):
            return "mobile_application"
        elif any(word in desc_lower for word in ["api", "rest", "graphql", "backend"]):
            return "api_service"
        elif any(word in desc_lower for word in ["chatbot", "bot", "ai assistant"]):
            return "chatbot"
        elif any(word in desc_lower for word in ["dashboard", "analytics", "data"]):
            return "dashboard"
        elif any(word in desc_lower for word in ["game", "gaming", "spiel"]):
            return "game"
        else:
            return "general_software"
    
    async def review_output(self, output: dict, reviewer: str = "") -> dict:
        """Review generated requirements."""
        review_prompt = f"""Review these requirements for:
1. Completeness - Are all necessary requirements covered?
2. Clarity - Are they unambiguous and testable?
3. Consistency - No contradictions
4. Feasibility - Can they be implemented?

Requirements to review:
{output.get('requirements_analysis', '')}

Provide a brief review with approval status and any concerns."""
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior requirements analyst reviewing work."},
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
