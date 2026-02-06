"""Testing Agent for test generation and quality assurance.

This agent specializes in:
- Generating unit tests
- Creating integration tests
- Writing test documentation
- Suggesting test strategies
- Code coverage analysis
"""

import structlog
from typing import Optional

import litellm

from noode.core.base_agent import Action, BaseAgent, Result
from noode.utils.validation import sanitize_for_prompt

logger = structlog.get_logger()


class TestingAgent(BaseAgent):
    """Agent for test generation and quality assurance."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        confidence_threshold: float = 0.7,
    ):
        super().__init__(
            name="testing_agent",
            role="Testing and Quality Assurance Specialist",
            capabilities=[
                "generate_unit_tests",
                "generate_integration_tests",
                "analyze_coverage",
            ],
            model=model,
            api_key=api_key,
            confidence_threshold=confidence_threshold,
        )
        
        self.system_prompt = """You are a Testing and Quality Assurance Specialist.

Your role is to:
1. Generate comprehensive test suites
2. Design integration and E2E tests
3. Ensure code quality through testing
4. Create test documentation
5. Suggest testing strategies and tools

Expertise:
- Unit testing (pytest, Jest, etc.)
- Integration testing
- End-to-End testing
- Test-driven development (TDD)
- Behavior-driven development (BDD)
- Test coverage analysis
- Mocking and stubbing
- Performance testing

Always:
- Write clear, maintainable tests
- Cover edge cases and error conditions
- Follow testing best practices (AAA pattern)
- Include both positive and negative tests
- Think about test isolation
- Consider test performance
- Document test scenarios"""
    
    async def think(self, context: str) -> dict:
        """Analyze testing requirements."""
        logger.info("analyzing_testing_requirements", context_length=len(context))
        
        safe_context = sanitize_for_prompt(context)
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": f"""Analyze the following code/requirements and suggest a testing strategy:

{safe_context}

Please provide:
1. What types of tests are needed?
2. Key test scenarios
3. Testing approach recommendation
4. Tools/frameworks to use

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
        """Execute testing-related actions."""
        if action.type == "generate_unit_tests":
            return await self._generate_unit_tests(action.payload)
        elif action.type == "generate_integration_tests":
            return await self._generate_integration_tests(action.payload)
        elif action.type == "generate_e2e_tests":
            return await self._generate_e2e_tests(action.payload)
        elif action.type == "analyze_coverage":
            return await self._analyze_coverage(action.payload)
        else:
            return Result(
                success=False,
                data={},
                error=f"Unknown action type: {action.type}",
            )
    
    async def _generate_unit_tests(self, payload: dict) -> Result:
        """Generate unit tests for code."""
        try:
            code = payload.get("code", "")
            language = payload.get("language", "python")
            test_framework = payload.get("test_framework", "pytest")
            
            safe_code = sanitize_for_prompt(code)
            
            logger.info("generating_unit_tests", language=language, framework=test_framework)
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Generate comprehensive unit tests for the following {language} code:

```{language}
{safe_code}
```

Framework: {test_framework}

Provide:

## 1. Test File Structure
- Imports and setup
- Fixtures (if needed)
- Test organization

## 2. Unit Tests
For each function/method, provide tests for:
- Happy path (normal operation)
- Edge cases (boundaries, empty inputs)
- Error cases (exceptions, invalid inputs)
- Boundary conditions

Follow AAA pattern (Arrange, Act, Assert)
Include descriptive test names
Add docstrings/comments explaining what is tested

## 3. Mocking
Show how to mock external dependencies
Use appropriate mocking framework for {test_framework}

## 4. Parametrized Tests
Use parametrization for multiple similar test cases

## 5. Test Data
Provide test data/fixtures needed

Ensure tests are:
- Independent (no shared state)
- Deterministic (same result every time)
- Fast
- Readable and maintainable"""
                    }
                ],
                temperature=0.3,
            )
            
            tests = response.choices[0].message.content
            
            return Result(
                success=True,
                data={
                    "unit_tests": tests,
                    "language": language,
                    "framework": test_framework,
                },
            )
            
        except Exception as e:
            logger.error("unit_test_generation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _generate_integration_tests(self, payload: dict) -> Result:
        """Generate integration tests."""
        try:
            api_spec = payload.get("api_spec", "")
            components = payload.get("components", [])
            tech_stack = payload.get("tech_stack", {})
            
            safe_spec = sanitize_for_prompt(api_spec)
            
            logger.info("generating_integration_tests")
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Generate integration tests for:

API/Components:
{safe_spec}

Tech Stack:
{tech_stack}

Provide:

## 1. Integration Test Strategy
- What components to test together
- Test environment setup
- Database/test data management

## 2. API Integration Tests
Test these scenarios:
- Successful API calls
- Error responses (4xx, 5xx)
- Authentication/Authorization
- Request/response validation
- Rate limiting (if applicable)

## 3. Database Integration Tests
- CRUD operations
- Transaction handling
- Connection pooling
- Migration testing

## 4. External Service Integration
- Mock external APIs
- Test failure scenarios
- Retry logic
- Circuit breaker patterns

## 5. Test Setup/Teardown
- Database setup/cleanup
- Test fixtures
- Environment configuration

Use appropriate testing tools for the tech stack."""
                    }
                ],
                temperature=0.3,
            )
            
            tests = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"integration_tests": tests},
            )
            
        except Exception as e:
            logger.error("integration_test_generation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _generate_e2e_tests(self, payload: dict) -> Result:
        """Generate end-to-end tests."""
        try:
            user_flows = payload.get("user_flows", [])
            app_type = payload.get("app_type", "web")
            
            logger.info("generating_e2e_tests", app_type=app_type)
            
            flows_text = "\n".join([f"- {flow}" for flow in user_flows])
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Generate end-to-end tests for a {app_type} application.

User Flows to Test:
{flows_text}

Provide:

## 1. E2E Test Framework Setup
- Recommended framework (Cypress, Playwright, Selenium)
- Configuration
- Directory structure

## 2. Test Scenarios
For each user flow:
- Test steps (Gherkin style: Given/When/Then)
- Expected outcomes
- Page objects/selectors
- Test data

## 3. Authentication Flows
- Login/Logout tests
- Session management
- Token refresh

## 4. Cross-Browser/Device Tests
- Responsive design tests
- Mobile-specific tests (if applicable)
- Browser compatibility

## 5. Visual Regression Tests
- Screenshot comparisons
- Component rendering

## 6. Performance Tests
- Page load times
- Interaction responsiveness
- API response times

## 7. CI/CD Integration
- How to run in CI
- Parallel execution
- Test reporting

Make tests resilient to UI changes using stable selectors."""
                    }
                ],
                temperature=0.3,
            )
            
            tests = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"e2e_tests": tests},
            )
            
        except Exception as e:
            logger.error("e2e_test_generation_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def _analyze_coverage(self, payload: dict) -> Result:
        """Analyze test coverage and suggest improvements."""
        try:
            code = payload.get("code", "")
            existing_tests = payload.get("existing_tests", "")
            coverage_report = payload.get("coverage_report", "")
            
            safe_code = sanitize_for_prompt(code)
            safe_tests = sanitize_for_prompt(existing_tests)
            
            logger.info("analyzing_coverage")
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {
                        "role": "user",
                        "content": f"""Analyze test coverage and suggest improvements.

Code:
```
{safe_code}
```

Existing Tests:
```
{safe_tests}
```

Coverage Report:
```
{coverage_report}
```

Provide:

## 1. Coverage Analysis
- Overall coverage percentage
- Coverage by module/function
- Critical uncovered areas

## 2. Missing Test Scenarios
- Happy paths not tested
- Edge cases missing
- Error conditions not covered

## 3. Test Quality Issues
- Brittle tests (implementation-dependent)
- Slow tests
- Tests with side effects
- Duplicate test logic

## 4. Recommendations
Priority list of:
- Tests to add (high priority)
- Tests to refactor
- Areas needing more coverage

## 5. Coverage Goals
- Target coverage percentages
- Critical path coverage
- Minimum acceptable coverage

## 6. Testing Tools
- Coverage tools to use
- Static analysis recommendations
- Mutation testing suggestions"""
                    }
                ],
                temperature=0.3,
            )
            
            analysis = response.choices[0].message.content
            
            return Result(
                success=True,
                data={"coverage_analysis": analysis},
            )
            
        except Exception as e:
            logger.error("coverage_analysis_failed", error=str(e))
            return Result(
                success=False,
                data={},
                error=str(e),
            )
    
    async def review_output(self, output: dict, reviewer: str = "") -> dict:
        """Review generated tests."""
        review_prompt = f"""Review these tests for:
1. Completeness (all scenarios covered)
2. Correctness (tests verify expected behavior)
3. Maintainability (clear, DRY principles)
4. Performance (tests are fast)
5. Independence (no shared state)

Tests to review:
{output.get('unit_tests', '')}

Provide approval status and suggestions."""
        
        response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a senior QA engineer reviewing tests."},
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
