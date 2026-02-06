"""Security Agent for vulnerability detection and compliance.

The Security Agent is responsible for:
- Scanning code for security vulnerabilities
- Checking dependencies for known CVEs
- Validating authentication and authorization
- Enforcing security by design principles
- Veto power on security-critical decisions
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import litellm
import structlog

from noode.core.base_agent import Action, BaseAgent, Result
from noode.protocols.messages import AgentMessage, MessageType
from noode.protocols.consensus import Vote, VoteType

logger = structlog.get_logger()


class Severity(Enum):
    """Security issue severity levels."""
    
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class VulnerabilityType(Enum):
    """Common vulnerability types."""
    
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    SENSITIVE_DATA = "sensitive_data"
    DEPENDENCY = "dependency"
    CONFIGURATION = "configuration"
    CRYPTOGRAPHY = "cryptography"
    INPUT_VALIDATION = "input_validation"


@dataclass
class SecurityFinding:
    """A security vulnerability or concern."""
    
    finding_id: str
    vulnerability_type: VulnerabilityType
    severity: Severity
    title: str
    description: str
    location: str  # file:line or component
    recommendation: str
    cwe_id: str | None = None  # Common Weakness Enumeration
    cvss_score: float | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class SecurityReport:
    """Complete security analysis report."""
    
    scan_id: str
    target: str  # What was scanned
    findings: list[SecurityFinding]
    passed: bool
    risk_score: float  # 0-10
    recommendations: list[str]
    scan_duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
    
    @property
    def high_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)


class SecurityAgent(BaseAgent):
    """Agent specialized in security analysis and enforcement.
    
    Has VETO POWER on all changes that introduce security vulnerabilities.
    Operates with unlimited budget for security reviews.
    """
    
    # Patterns to check for common vulnerabilities
    VULNERABILITY_PATTERNS = {
        VulnerabilityType.SQL_INJECTION: [
            r"execute\s*\(\s*['\"].*\%",
            r"cursor\.execute\s*\(\s*f['\"]",
            r"query\s*=\s*['\"].*\+",
        ],
        VulnerabilityType.XSS: [
            r"innerHTML\s*=",
            r"document\.write\s*\(",
            r"dangerouslySetInnerHTML",
        ],
        VulnerabilityType.SENSITIVE_DATA: [
            r"password\s*=\s*['\"][^'\"]+['\"]",
            r"api_key\s*=\s*['\"][^'\"]+['\"]",
            r"secret\s*=\s*['\"][^'\"]+['\"]",
        ],
        VulnerabilityType.AUTHENTICATION: [
            r"verify\s*=\s*False",
            r"check_password.*==",  # Timing attack
        ],
    }
    
    def __init__(
        self,
        name: str = "security_agent",
        model: str = "gpt-4o",
    ) -> None:
        """Initialize the security agent.
        
        Args:
            name: Agent name
            model: LLM model to use
        """
        super().__init__(
            name=name,
            role="Security Analysis and Enforcement Specialist",
            capabilities=[
                "vulnerability scanning",
                "dependency auditing",
                "security code review",
                "compliance validation",
                "threat modeling",
                "security veto",
            ],
            model=model,
            confidence_threshold=0.9,  # High threshold for security decisions
        )
        self._vulnerability_db: dict[str, list[str]] = {}  # CVE cache
    
    async def act(self, action: Action) -> Result:
        """Execute a security action.
        
        Args:
            action: The action to execute
            
        Returns:
            Result of the security analysis
        """
        start_time = datetime.now()
        
        try:
            if action.action_type == "scan_code":
                report = await self.scan_code(
                    code=action.parameters.get("code", ""),
                    filename=action.parameters.get("filename", "unknown"),
                    language=action.parameters.get("language", "python"),
                )
                return Result(
                    success=True,
                    output=report,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "review_change":
                vote = await self.review_change(
                    diff=action.parameters.get("diff", ""),
                    context=action.parameters.get("context", {}),
                )
                return Result(
                    success=True,
                    output=vote,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            elif action.action_type == "audit_dependencies":
                findings = await self.audit_dependencies(
                    dependencies=action.parameters.get("dependencies", {}),
                )
                return Result(
                    success=True,
                    output=findings,
                    duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
                )
            
            else:
                return Result(
                    success=False,
                    output=None,
                    error=f"Unknown action type: {action.action_type}",
                )
                
        except Exception as e:
            logger.error("security_action_failed", error=str(e))
            return Result(
                success=False,
                output=None,
                error=str(e),
                duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )
    
    async def scan_code(
        self,
        code: str,
        filename: str,
        language: str = "python",
    ) -> SecurityReport:
        """Scan code for security vulnerabilities.
        
        Args:
            code: Source code to scan
            filename: Name of the file
            language: Programming language
            
        Returns:
            Security report with findings
        """
        import re
        import uuid
        
        start_time = datetime.now()
        scan_id = str(uuid.uuid4())[:8]
        findings: list[SecurityFinding] = []
        
        logger.info("security_scan_started", filename=filename, scan_id=scan_id)
        
        # 1. Pattern-based scanning
        for vuln_type, patterns in self.VULNERABILITY_PATTERNS.items():
            for pattern in patterns:
                for i, line in enumerate(code.split("\n"), 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append(SecurityFinding(
                            finding_id=f"{scan_id}-{len(findings)}",
                            vulnerability_type=vuln_type,
                            severity=self._get_severity(vuln_type),
                            title=f"Potential {vuln_type.value.replace('_', ' ').title()}",
                            description=f"Pattern match detected: {pattern}",
                            location=f"{filename}:{i}",
                            recommendation=self._get_recommendation(vuln_type),
                        ))
        
        # 2. LLM-based deep analysis
        llm_findings = await self._llm_security_analysis(code, filename, language)
        findings.extend(llm_findings)
        
        # 3. Calculate risk score
        risk_score = self._calculate_risk_score(findings)
        
        # 4. Determine pass/fail
        passed = risk_score < 5.0 and all(
            f.severity not in (Severity.CRITICAL, Severity.HIGH) 
            for f in findings
        )
        
        report = SecurityReport(
            scan_id=scan_id,
            target=filename,
            findings=findings,
            passed=passed,
            risk_score=risk_score,
            recommendations=self._generate_recommendations(findings),
            scan_duration_ms=(datetime.now() - start_time).total_seconds() * 1000,
        )
        
        logger.info(
            "security_scan_completed",
            scan_id=scan_id,
            findings=len(findings),
            passed=passed,
            risk_score=risk_score,
        )
        
        return report
    
    async def review_change(
        self,
        diff: str,
        context: dict[str, Any],
    ) -> Vote:
        """Review a code change for security implications.
        
        This is where the Security Agent exercises its VETO power.
        
        Args:
            diff: The code diff to review
            context: Additional context about the change
            
        Returns:
            Vote with approval/rejection and reasoning
        """
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": f"""{self.system_prompt}

You are conducting a SECURITY REVIEW. You have VETO POWER.
If you identify ANY of these issues, you MUST REJECT:
- SQL injection vulnerabilities
- Cross-site scripting (XSS)
- Authentication/authorization bypasses
- Sensitive data exposure
- Insecure cryptography
- Known vulnerable dependencies

Be thorough. Security is the highest priority.""",
            }, {
                "role": "user",
                "content": f"""Review this code change for security issues:

Context: {context}

Diff:
```
{diff}
```

Analyze for:
1. Security vulnerabilities introduced
2. Security best practices violated
3. Potential attack vectors
4. Missing security controls

Decision: APPROVE (no security issues) or REJECT (security issues found)
Provide detailed reasoning.""",
            }],
            temperature=0.2,  # Low temperature for consistent security decisions
        )
        
        content = response.choices[0].message.content or ""
        
        # Determine approval based on response
        is_rejection = any(word in content.lower() for word in [
            "reject", "veto", "vulnerability", "critical", "high risk",
            "injection", "bypass", "exposed", "insecure"
        ])
        
        concerns = []
        if is_rejection:
            # Extract concerns from response
            for line in content.split("\n"):
                line = line.strip()
                if line.startswith("-") or line.startswith("*"):
                    concerns.append(line.lstrip("-* "))
        
        vote = Vote(
            voter=self.name,
            vote_type=VoteType.REJECT if is_rejection else VoteType.APPROVE,
            confidence=0.95 if is_rejection else 0.8,
            reasoning=content[:500],
            concerns=concerns[:5],  # Top 5 concerns
        )
        
        if is_rejection:
            logger.warning(
                "security_veto",
                concerns=concerns[:3],
            )
        
        return vote
    
    async def audit_dependencies(
        self,
        dependencies: dict[str, str],
    ) -> list[SecurityFinding]:
        """Audit dependencies for known vulnerabilities.
        
        Args:
            dependencies: Dict of package name -> version
            
        Returns:
            List of security findings for vulnerable deps
        """
        findings: list[SecurityFinding] = []
        
        # Use LLM to check for known vulnerabilities
        # In production, this would query actual CVE databases
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": """You are a security expert checking dependencies for 
known vulnerabilities. Check each package version against known CVEs.""",
            }, {
                "role": "user",
                "content": f"""Check these dependencies for known vulnerabilities:

{chr(10).join(f'{pkg}: {ver}' for pkg, ver in dependencies.items())}

For each vulnerable package, provide:
- Package name and version
- CVE ID if known
- Severity (critical/high/medium/low)
- Recommended version""",
            }],
            temperature=0.2,
        )
        
        content = response.choices[0].message.content or ""
        
        # Parse findings (simplified)
        lines = content.split("\n")
        for line in lines:
            if "cve" in line.lower() or "vulnerability" in line.lower():
                findings.append(SecurityFinding(
                    finding_id=f"dep-{len(findings)}",
                    vulnerability_type=VulnerabilityType.DEPENDENCY,
                    severity=Severity.HIGH,
                    title="Vulnerable Dependency",
                    description=line,
                    location="dependencies",
                    recommendation="Upgrade to patched version",
                ))
        
        return findings
    
    async def _llm_security_analysis(
        self,
        code: str,
        filename: str,
        language: str,
    ) -> list[SecurityFinding]:
        """Deep security analysis using LLM."""
        response = await litellm.acompletion(
            model=self.model,
            messages=[{
                "role": "system",
                "content": self.system_prompt,
            }, {
                "role": "user",
                "content": f"""Perform a comprehensive security analysis of this {language} code:

File: {filename}
```{language}
{code[:3000]}  # Limit code length
```

Check for:
1. OWASP Top 10 vulnerabilities
2. Language-specific security issues
3. Authentication/authorization flaws
4. Data validation issues
5. Cryptographic weaknesses
6. Error handling that leaks information

For each issue found, provide:
- Severity (critical/high/medium/low)
- Line number if possible
- Description
- Recommendation""",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or ""
        findings: list[SecurityFinding] = []
        
        # Parse LLM findings
        current_severity = Severity.MEDIUM
        for line in content.split("\n"):
            line = line.strip().lower()
            
            if "critical" in line:
                current_severity = Severity.CRITICAL
            elif "high" in line:
                current_severity = Severity.HIGH
            elif "medium" in line:
                current_severity = Severity.MEDIUM
            elif "low" in line:
                current_severity = Severity.LOW
            
            # Look for issue indicators
            if any(word in line for word in ["vulnerability", "issue", "flaw", "weakness"]):
                findings.append(SecurityFinding(
                    finding_id=f"llm-{len(findings)}",
                    vulnerability_type=VulnerabilityType.INPUT_VALIDATION,
                    severity=current_severity,
                    title="LLM-Detected Security Issue",
                    description=line[:200],
                    location=filename,
                    recommendation="Review and remediate",
                ))
        
        return findings[:10]  # Limit to top 10 LLM findings
    
    def _get_severity(self, vuln_type: VulnerabilityType) -> Severity:
        """Get default severity for vulnerability type."""
        severity_map = {
            VulnerabilityType.SQL_INJECTION: Severity.CRITICAL,
            VulnerabilityType.XSS: Severity.HIGH,
            VulnerabilityType.AUTHENTICATION: Severity.CRITICAL,
            VulnerabilityType.AUTHORIZATION: Severity.CRITICAL,
            VulnerabilityType.SENSITIVE_DATA: Severity.HIGH,
            VulnerabilityType.CRYPTOGRAPHY: Severity.HIGH,
            VulnerabilityType.CSRF: Severity.MEDIUM,
            VulnerabilityType.CONFIGURATION: Severity.MEDIUM,
            VulnerabilityType.DEPENDENCY: Severity.HIGH,
            VulnerabilityType.INPUT_VALIDATION: Severity.MEDIUM,
        }
        return severity_map.get(vuln_type, Severity.MEDIUM)
    
    def _get_recommendation(self, vuln_type: VulnerabilityType) -> str:
        """Get remediation recommendation for vulnerability type."""
        recommendations = {
            VulnerabilityType.SQL_INJECTION: "Use parameterized queries or ORM",
            VulnerabilityType.XSS: "Sanitize user input, use CSP headers",
            VulnerabilityType.AUTHENTICATION: "Use secure password hashing, implement MFA",
            VulnerabilityType.AUTHORIZATION: "Implement proper RBAC, validate permissions",
            VulnerabilityType.SENSITIVE_DATA: "Use environment variables, encrypt at rest",
            VulnerabilityType.CRYPTOGRAPHY: "Use vetted libraries, avoid deprecated algorithms",
            VulnerabilityType.CSRF: "Implement CSRF tokens",
            VulnerabilityType.CONFIGURATION: "Review security configuration",
            VulnerabilityType.DEPENDENCY: "Update to patched version",
            VulnerabilityType.INPUT_VALIDATION: "Validate and sanitize all inputs",
        }
        return recommendations.get(vuln_type, "Review and remediate")
    
    def _calculate_risk_score(self, findings: list[SecurityFinding]) -> float:
        """Calculate overall risk score (0-10)."""
        if not findings:
            return 0.0
        
        severity_weights = {
            Severity.CRITICAL: 3.0,
            Severity.HIGH: 2.0,
            Severity.MEDIUM: 1.0,
            Severity.LOW: 0.5,
            Severity.INFO: 0.1,
        }
        
        total_weight = sum(severity_weights[f.severity] for f in findings)
        
        # Normalize to 0-10 scale
        return min(10.0, total_weight)
    
    def _generate_recommendations(
        self,
        findings: list[SecurityFinding],
    ) -> list[str]:
        """Generate prioritized recommendations."""
        recommendations = []
        
        # Group by severity
        critical = [f for f in findings if f.severity == Severity.CRITICAL]
        high = [f for f in findings if f.severity == Severity.HIGH]
        
        if critical:
            recommendations.append(
                f"🔴 CRITICAL: Fix {len(critical)} critical issues immediately"
            )
        
        if high:
            recommendations.append(
                f"🟠 HIGH: Address {len(high)} high-severity issues"
            )
        
        # Add specific recommendations
        seen = set()
        for f in findings:
            if f.recommendation not in seen:
                recommendations.append(f.recommendation)
                seen.add(f.recommendation)
        
        return recommendations[:10]
