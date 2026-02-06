"""CI/CD integration for Noode.

Provides GitHub Actions workflows and CI/CD hooks.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger()


@dataclass
class WorkflowStep:
    """A step in a CI/CD workflow."""
    
    name: str
    run: str | None = None
    uses: str | None = None
    with_: dict[str, Any] | None = None
    env: dict[str, str] | None = None


@dataclass
class WorkflowJob:
    """A job in a CI/CD workflow."""
    
    name: str
    runs_on: str = "ubuntu-latest"
    steps: list[WorkflowStep] | None = None


@dataclass
class Workflow:
    """A CI/CD workflow definition."""
    
    name: str
    on: dict[str, Any]
    jobs: dict[str, WorkflowJob]


class CICDGenerator:
    """Generate CI/CD configurations."""
    
    def __init__(self) -> None:
        """Initialize CI/CD generator."""
        self.templates: dict[str, Workflow] = {
            "python": self._python_workflow(),
            "node": self._node_workflow(),
            "docker": self._docker_workflow(),
            "noode": self._noode_workflow(),
        }
    
    def generate_github_actions(
        self,
        project_path: Path,
        template: str = "noode",
    ) -> Path:
        """Generate GitHub Actions workflow.
        
        Args:
            project_path: Project directory
            template: Workflow template to use
            
        Returns:
            Path to generated workflow file
        """
        workflow = self.templates.get(template)
        if not workflow:
            workflow = self.templates["noode"]
        
        workflows_dir = project_path / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_file = workflows_dir / "noode.yml"
        workflow_file.write_text(self._render_workflow(workflow))
        
        logger.info(
            "workflow_generated",
            path=str(workflow_file),
            template=template,
        )
        
        return workflow_file
    
    def generate_pre_commit(self, project_path: Path) -> Path:
        """Generate pre-commit configuration.
        
        Args:
            project_path: Project directory
            
        Returns:
            Path to generated config
        """
        config = """# Noode Pre-commit Configuration
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.4.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: local
    hooks:
      - id: noode-security
        name: Noode Security Review
        entry: noode review
        language: system
        types: [python]
        pass_filenames: true
"""
        
        config_file = project_path / ".pre-commit-config.yaml"
        config_file.write_text(config)
        
        return config_file
    
    def _python_workflow(self) -> Workflow:
        """Python CI workflow template."""
        return Workflow(
            name="Python CI",
            on={
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
            },
            jobs={
                "test": WorkflowJob(
                    name="Test",
                    runs_on="ubuntu-latest",
                    steps=[
                        WorkflowStep(name="Checkout", uses="actions/checkout@v4"),
                        WorkflowStep(
                            name="Setup Python",
                            uses="actions/setup-python@v5",
                            with_={"python-version": "3.12"},
                        ),
                        WorkflowStep(
                            name="Install dependencies",
                            run="pip install -e .[dev]",
                        ),
                        WorkflowStep(
                            name="Run tests",
                            run="pytest tests/ -v",
                        ),
                    ],
                ),
            },
        )
    
    def _node_workflow(self) -> Workflow:
        """Node.js CI workflow template."""
        return Workflow(
            name="Node CI",
            on={
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
            },
            jobs={
                "test": WorkflowJob(
                    name="Test",
                    runs_on="ubuntu-latest",
                    steps=[
                        WorkflowStep(name="Checkout", uses="actions/checkout@v4"),
                        WorkflowStep(
                            name="Setup Node",
                            uses="actions/setup-node@v4",
                            with_={"node-version": "20"},
                        ),
                        WorkflowStep(name="Install", run="npm ci"),
                        WorkflowStep(name="Test", run="npm test"),
                    ],
                ),
            },
        )
    
    def _docker_workflow(self) -> Workflow:
        """Docker build workflow template."""
        return Workflow(
            name="Docker Build",
            on={
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
            },
            jobs={
                "build": WorkflowJob(
                    name="Build",
                    runs_on="ubuntu-latest",
                    steps=[
                        WorkflowStep(name="Checkout", uses="actions/checkout@v4"),
                        WorkflowStep(
                            name="Set up Docker Buildx",
                            uses="docker/setup-buildx-action@v3",
                        ),
                        WorkflowStep(
                            name="Build",
                            run="docker build -t app .",
                        ),
                    ],
                ),
            },
        )
    
    def _noode_workflow(self) -> Workflow:
        """Noode-specific CI workflow."""
        return Workflow(
            name="Noode CI",
            on={
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
            },
            jobs={
                "security": WorkflowJob(
                    name="Security Review",
                    runs_on="ubuntu-latest",
                    steps=[
                        WorkflowStep(name="Checkout", uses="actions/checkout@v4"),
                        WorkflowStep(
                            name="Setup Python",
                            uses="actions/setup-python@v5",
                            with_={"python-version": "3.12"},
                        ),
                        WorkflowStep(
                            name="Install Noode",
                            run="pip install noode",
                        ),
                        WorkflowStep(
                            name="Security Review",
                            run="noode review src/",
                            env={"OPENAI_API_KEY": "${{ secrets.OPENAI_API_KEY }}"},
                        ),
                    ],
                ),
                "test": WorkflowJob(
                    name="Test",
                    runs_on="ubuntu-latest",
                    steps=[
                        WorkflowStep(name="Checkout", uses="actions/checkout@v4"),
                        WorkflowStep(
                            name="Setup Python",
                            uses="actions/setup-python@v5",
                            with_={"python-version": "3.12"},
                        ),
                        WorkflowStep(
                            name="Install dependencies",
                            run="pip install -e .[dev]",
                        ),
                        WorkflowStep(
                            name="Run tests",
                            run="pytest tests/ -v",
                        ),
                    ],
                ),
            },
        )
    
    def _render_workflow(self, workflow: Workflow) -> str:
        """Render workflow to YAML string."""
        lines = [
            f"name: {workflow.name}",
            "",
            "on:",
        ]
        
        # Render triggers
        for trigger, config in workflow.on.items():
            if isinstance(config, dict):
                lines.append(f"  {trigger}:")
                for key, value in config.items():
                    if isinstance(value, list):
                        lines.append(f"    {key}: [{', '.join(value)}]")
                    else:
                        lines.append(f"    {key}: {value}")
            else:
                lines.append(f"  {trigger}: {config}")
        
        lines.append("")
        lines.append("jobs:")
        
        # Render jobs
        for job_id, job in workflow.jobs.items():
            lines.append(f"  {job_id}:")
            lines.append(f"    name: {job.name}")
            lines.append(f"    runs-on: {job.runs_on}")
            lines.append("    steps:")
            
            if job.steps:
                for step in job.steps:
                    lines.append(f"      - name: {step.name}")
                    
                    if step.uses:
                        lines.append(f"        uses: {step.uses}")
                    
                    if step.with_:
                        lines.append("        with:")
                        for key, value in step.with_.items():
                            lines.append(f"          {key}: {value}")
                    
                    if step.run:
                        lines.append(f"        run: {step.run}")
                    
                    if step.env:
                        lines.append("        env:")
                        for key, value in step.env.items():
                            lines.append(f"          {key}: {value}")
        
        return "\n".join(lines) + "\n"
