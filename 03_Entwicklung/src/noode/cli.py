"""Noode CLI - Command Line Interface for project management."""

import asyncio
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, Confirm

app = typer.Typer(
    name="noode",
    help="🚀 Autonomous Development Platform - Build software with AI agents",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init(
    name: Annotated[str, typer.Argument(help="Project name")] = "",
    template: Annotated[str, typer.Option("--template", "-t", help="Project template")] = "web-app",
    path: Annotated[Path, typer.Option("--path", "-p", help="Project path")] = Path("."),
) -> None:
    """Initialize a new Noode project with AI agents."""
    
    console.print(Panel.fit(
        "[bold blue]🚀 Noode Project Initializer[/bold blue]\n"
        "Create a new project with autonomous AI agents",
        border_style="blue",
    ))
    
    # Get project name interactively if not provided
    if not name:
        name = Prompt.ask("[cyan]Project name[/cyan]")
    
    project_path = path / name
    
    console.print(f"\n📁 Creating project: [bold]{name}[/bold]")
    console.print(f"📍 Location: [dim]{project_path.absolute()}[/dim]")
    console.print(f"📋 Template: [green]{template}[/green]\n")
    
    if project_path.exists():
        if not Confirm.ask(f"[yellow]Directory exists. Continue?[/yellow]"):
            raise typer.Abort()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Create project structure
        task = progress.add_task("Creating V-Model XT structure...", total=None)
        _create_project_structure(project_path, template)
        progress.update(task, completed=True)
        
        # Initialize agents
        task = progress.add_task("Initializing AI agents...", total=None)
        asyncio.run(_init_agents(project_path))
        progress.update(task, completed=True)
        
        # Setup environment
        task = progress.add_task("Setting up environment...", total=None)
        _setup_environment(project_path)
        progress.update(task, completed=True)
    
    console.print(Panel.fit(
        f"[bold green]✅ Project '{name}' created successfully![/bold green]\n\n"
        f"Next steps:\n"
        f"  cd {name}\n"
        f"  noode agents status\n"
        f"  noode run 'Erstelle eine Login-Seite'",
        border_style="green",
    ))


@app.command()
def run(
    task: Annotated[str, typer.Argument(help="Task to execute in natural language")],
    agent: Annotated[str, typer.Option("--agent", "-a", help="Specific agent to use")] = "auto",
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Show plan without executing")] = False,
) -> None:
    """Execute a development task using AI agents."""
    
    console.print(Panel.fit(
        f"[bold cyan]🤖 Task: {task}[/bold cyan]",
        border_style="cyan",
    ))
    
    if dry_run:
        console.print("[yellow]Dry run mode - showing plan only[/yellow]\n")
    
    asyncio.run(_execute_task(task, agent, dry_run))


@app.command()
def agents() -> None:
    """Show status of all AI agents."""
    
    table = Table(title="🤖 Agent Status")
    table.add_column("Agent", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Capabilities", style="dim")
    
    agents_info = [
        ("Research", "Information Specialist", "🟢 Ready", "Search, Analysis"),
        ("Security", "Security Enforcement", "🟢 Ready", "Scanning, Veto"),
        ("Frontend", "UI/UX Development", "🟢 Ready", "React, CSS"),
        ("Backend", "API Development", "🟢 Ready", "FastAPI, DB"),
    ]
    
    for agent in agents_info:
        table.add_row(*agent)
    
    console.print(table)


@app.command()
def review(
    path: Annotated[Path, typer.Argument(help="File or directory to review")] = Path("."),
) -> None:
    """Run security review on code."""
    
    console.print(f"[cyan]🔍 Security review: {path}[/cyan]\n")
    asyncio.run(_run_security_review(path))


@app.command()
def generate(
    component: Annotated[str, typer.Argument(help="Component to generate")],
    name: Annotated[str, typer.Option("--name", "-n", help="Component name")] = "",
) -> None:
    """Generate code components using AI agents."""
    
    console.print(f"[cyan]⚡ Generating {component}...[/cyan]\n")
    asyncio.run(_generate_component(component, name))


@app.command()
def server(
    host: Annotated[str, typer.Option("--host", "-h", help="Host to bind")] = "0.0.0.0",
    port: Annotated[int, typer.Option("--port", "-p", help="Port to listen on")] = 8000,
    reload: Annotated[bool, typer.Option("--reload", help="Enable auto-reload")] = False,
) -> None:
    """Start the Noode API server."""
    
    console.print(Panel.fit(
        f"[bold green]🚀 Starting Noode API Server[/bold green]\n"
        f"Host: {host}\n"
        f"Port: {port}\n"
        f"Reload: {reload}",
        border_style="green",
    ))
    
    import uvicorn
    uvicorn.run(
        "noode.api.server:app",
        host=host,
        port=port,
        reload=reload,
    )


# Internal functions

def _create_project_structure(path: Path, template: str) -> None:
    """Create V-Model XT project structure."""
    
    directories = [
        "00_Projektmanagement",
        "01_Anforderungen",
        "02_Systemarchitektur",
        "03_Entwicklung/src",
        "03_Entwicklung/tests",
        "04_Test/Testfälle",
        "04_Test/Testprotokolle",
        "05_Qualitätssicherung",
        "06_Lieferung",
        ".noode/agents",
        ".noode/knowledge",
    ]
    
    for dir_name in directories:
        (path / dir_name).mkdir(parents=True, exist_ok=True)
    
    # Create noode.yaml config
    config = f"""# Noode Project Configuration
project:
  name: {path.name}
  template: {template}
  version: 0.1.0

agents:
  research:
    enabled: true
    model: gpt-4o
  security:
    enabled: true
    veto_enabled: true
  frontend:
    enabled: true
    framework: react
  backend:
    enabled: true
    framework: fastapi
    database: postgresql

knowledge:
  storage: local
  embedding_model: text-embedding-3-small
"""
    (path / "noode.yaml").write_text(config)
    
    # Create README
    readme = f"""# {path.name}

Created with [Noode](https://github.com/noode-ai/noode) - Autonomous Development Platform

## Getting Started

```bash
# Show agent status
noode agents

# Execute a task
noode run 'Create a user authentication system'

# Security review
noode review src/
```

## Project Structure

```
{path.name}/
├── 00_Projektmanagement/  # Project management docs
├── 01_Anforderungen/      # Requirements
├── 02_Systemarchitektur/  # Architecture
├── 03_Entwicklung/        # Development
├── 04_Test/               # Testing
├── 05_Qualitätssicherung/ # Quality assurance
├── 06_Lieferung/          # Delivery
└── .noode/                # Agent configuration
```
"""
    (path / "README.md").write_text(readme)


async def _init_agents(path: Path) -> None:
    """Initialize agent configurations."""
    from noode.agents import ResearchAgent, SecurityAgent, FrontendAgent, BackendAgent
    from noode.core import KnowledgeStore
    
    # Initialize knowledge store
    knowledge_path = path / ".noode" / "knowledge"
    store = KnowledgeStore(storage_path=knowledge_path)
    
    # Add initial knowledge about the project
    await store.add(
        content=f"Project {path.name} initialized with web-app template",
        entry_type="project",
        source="init",
    )


def _setup_environment(path: Path) -> None:
    """Setup development environment."""
    
    # Create .env template
    env_template = """# Noode Environment Configuration

# LLM API (required)
OPENAI_API_KEY=your_api_key_here

# Optional: Alternative providers
# ANTHROPIC_API_KEY=
# GOOGLE_API_KEY=

# Development
DEBUG=false
LOG_LEVEL=info
"""
    (path / ".env.example").write_text(env_template)
    
    # Create gitignore
    gitignore = """.env
.venv/
__pycache__/
*.pyc
.noode/knowledge/*.json
.DS_Store
"""
    (path / ".gitignore").write_text(gitignore)


async def _execute_task(task: str, agent: str, dry_run: bool) -> None:
    """Execute a task using agents."""
    from noode.core import Orchestrator
    from noode.agents import ResearchAgent, SecurityAgent, FrontendAgent, BackendAgent
    
    # Initialize orchestrator
    orchestrator = Orchestrator()
    
    # Register agents
    orchestrator.register_agent(ResearchAgent())
    orchestrator.register_agent(SecurityAgent())
    orchestrator.register_agent(FrontendAgent())
    orchestrator.register_agent(BackendAgent())
    
    # Create project
    project = orchestrator.create_project("current", "Current", task)
    
    # Decompose task
    console.print("[dim]Analyzing task...[/dim]")
    subtasks = await orchestrator.decompose_task("main", task, "current")
    
    console.print(f"\n[bold]📋 Task decomposed into {len(subtasks)} subtasks:[/bold]")
    for i, subtask in enumerate(subtasks, 1):
        console.print(f"  {i}. {subtask.description[:60]}...")
        if subtask.assigned_agent:
            console.print(f"     [dim]→ {subtask.assigned_agent}[/dim]")
    
    if dry_run:
        console.print("\n[yellow]Dry run complete. Use without --dry-run to execute.[/yellow]")
        return
    
    # Execute subtasks
    console.print("\n[bold]⚡ Executing tasks...[/bold]\n")
    
    for subtask in subtasks:
        with console.status(f"[cyan]{subtask.description[:50]}...[/cyan]"):
            if await orchestrator.assign_task(subtask):
                console.print(f"  [green]✓[/green] {subtask.description[:60]}")
            else:
                console.print(f"  [red]✗[/red] {subtask.description[:60]}")


async def _run_security_review(path: Path) -> None:
    """Run security review on path."""
    from noode.agents import SecurityAgent
    
    agent = SecurityAgent()
    
    # Find Python files
    files = list(path.rglob("*.py")) if path.is_dir() else [path]
    
    total_findings = 0
    
    for file in files[:10]:  # Limit for demo
        if file.exists():
            code = file.read_text()
            report = await agent.scan_code(code, str(file))
            
            if report.findings:
                console.print(f"\n[yellow]{file}[/yellow]")
                for finding in report.findings[:3]:
                    console.print(f"  [{finding.severity.value}] {finding.title}")
                total_findings += len(report.findings)
    
    if total_findings == 0:
        console.print("[green]✅ No security issues found![/green]")
    else:
        console.print(f"\n[yellow]⚠️ Found {total_findings} potential issues[/yellow]")


async def _generate_component(component: str, name: str) -> None:
    """Generate a component using appropriate agent."""
    from noode.agents import FrontendAgent, BackendAgent
    
    component_lower = component.lower()
    
    if component_lower in ["page", "component", "form", "modal"]:
        agent = FrontendAgent()
        from noode.agents.frontend_agent import ComponentType
        
        comp_type = {
            "page": ComponentType.PAGE,
            "component": ComponentType.CUSTOM,
            "form": ComponentType.FORM,
            "modal": ComponentType.MODAL,
        }.get(component_lower, ComponentType.CUSTOM)
        
        result = await agent.generate_component(
            description=name or f"A {component} component",
            component_type=comp_type,
        )
        
        console.print(f"\n[bold green]Generated: {result.name}[/bold green]\n")
        console.print(Panel(result.code[:500] + "...", title="Component Code"))
        
    elif component_lower in ["api", "endpoint", "service"]:
        agent = BackendAgent()
        
        result = await agent.design_api(
            description=name or f"A {component}",
            resources=[name] if name else ["resource"],
        )
        
        console.print(f"\n[bold green]API: {result.name}[/bold green]")
        console.print(f"Endpoints: {len(result.endpoints)}")


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
