"""Orchestrator for coordinating agent activities.

The Orchestrator is the central coordinator that:
- Decomposes tasks into subtasks
- Assigns work to specialized agents
- Manages dependencies between tasks
- Coordinates peer review processes
- Handles conflict resolution
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

from noode.core.base_agent import BaseAgent
from noode.protocols.consensus import ConsensusBuilder, Vote, VoteType
from noode.protocols.messages import (
    AgentMessage,
    MessageType,
    ReviewRequest,
    ReviewResult,
    TaskRequest,
    TaskResult,
)

logger = structlog.get_logger()


class TaskStatus(Enum):
    """Status of a task in the system."""
    
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class SubTask:
    """A decomposed subtask."""
    
    task_id: str
    parent_id: str | None
    description: str
    assigned_agent: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    dependencies: list[str] = field(default_factory=list)
    result: TaskResult | None = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: datetime | None = None


@dataclass
class ProjectState:
    """Current state of a project."""
    
    project_id: str
    name: str
    description: str
    tasks: dict[str, SubTask] = field(default_factory=dict)
    artifacts: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Central coordinator for agent activities.
    
    The Orchestrator manages the flow of work through the system,
    ensuring tasks are decomposed, assigned, reviewed, and completed
    in a coordinated manner.
    
    Attributes:
        agents: Registered specialized agents
        projects: Active projects being managed
    """
    
    def __init__(self) -> None:
        """Initialize the orchestrator."""
        self._agents: dict[str, BaseAgent] = {}
        self._projects: dict[str, ProjectState] = {}
        self._task_queue: asyncio.Queue[SubTask] = asyncio.Queue()
        self._message_queue: asyncio.Queue[AgentMessage] = asyncio.Queue()
        self._running = False
        
        logger.info("orchestrator_initialized")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the orchestrator.
        
        Args:
            agent: The agent to register
        """
        self._agents[agent.name] = agent
        logger.info("agent_registered", agent=agent.name, role=agent.role)
    
    def unregister_agent(self, name: str) -> None:
        """Unregister an agent.
        
        Args:
            name: Name of agent to unregister
        """
        if name in self._agents:
            del self._agents[name]
            logger.info("agent_unregistered", agent=name)
    
    def create_project(
        self,
        project_id: str,
        name: str,
        description: str,
    ) -> ProjectState:
        """Create a new project.
        
        Args:
            project_id: Unique project identifier
            name: Human-readable name
            description: Project description
            
        Returns:
            The created ProjectState
        """
        project = ProjectState(
            project_id=project_id,
            name=name,
            description=description,
        )
        self._projects[project_id] = project
        logger.info("project_created", project=project_id, name=name)
        return project
    
    async def decompose_task(
        self,
        task_id: str,
        description: str,
        project_id: str,
    ) -> list[SubTask]:
        """Decompose a high-level task into subtasks.
        
        Uses an LLM to analyze the task and break it down into
        smaller, agent-appropriate subtasks.
        
        Args:
            task_id: ID for the main task
            description: What needs to be done
            project_id: Project this task belongs to
            
        Returns:
            List of decomposed subtasks
        """
        logger.info("decomposing_task", task_id=task_id, description=description[:50])
        
        # Get available agent capabilities
        agent_capabilities = {
            name: agent.capabilities 
            for name, agent in self._agents.items()
        }
        
        # Use LLM to decompose (simplified - would use structured output)
        import litellm
        
        response = await litellm.acompletion(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": """You are a task decomposition expert. Break down tasks into 
subtasks that can be assigned to specialized agents.

Available agents and their capabilities:
""" + "\n".join(f"- {name}: {caps}" for name, caps in agent_capabilities.items()),
            }, {
                "role": "user",
                "content": f"""Decompose this task into subtasks:

{description}

For each subtask, specify:
1. Description
2. Which agent should handle it
3. Dependencies on other subtasks (if any)

Format as JSON array.""",
            }],
            temperature=0.3,
        )
        
        content = response.choices[0].message.content or "[]"
        
        # Parse subtasks (simplified)
        subtasks = self._parse_subtasks(task_id, content)
        
        # Add to project
        if project_id in self._projects:
            for subtask in subtasks:
                self._projects[project_id].tasks[subtask.task_id] = subtask
        
        logger.info("task_decomposed", task_id=task_id, subtask_count=len(subtasks))
        return subtasks
    
    async def assign_task(self, subtask: SubTask) -> bool:
        """Assign a subtask to an agent.
        
        Args:
            subtask: The subtask to assign
            
        Returns:
            True if assignment succeeded
        """
        if not subtask.assigned_agent:
            # Find best agent for task
            subtask.assigned_agent = self._select_agent(subtask)
        
        if subtask.assigned_agent not in self._agents:
            logger.error("agent_not_found", agent=subtask.assigned_agent)
            return False
        
        agent = self._agents[subtask.assigned_agent]
        
        # Create task request message
        request = TaskRequest(
            task_id=subtask.task_id,
            task_type="development",
            description=subtask.description,
        )
        
        message = AgentMessage(
            sender="orchestrator",
            receiver=agent.name,
            message_type=MessageType.REQUEST,
            content=request,
            confidence=1.0,
        )
        
        agent.receive_message(message)
        subtask.status = TaskStatus.ASSIGNED
        
        logger.info("task_assigned", task_id=subtask.task_id, agent=agent.name)
        return True
    
    async def coordinate_review(
        self,
        change_id: str,
        change: Any,
        author: str,
        reviewers: list[str] | None = None,
    ) -> ConsensusBuilder:
        """Coordinate a peer review process.
        
        Args:
            change_id: ID of the change to review
            change: The change content
            author: Who made the change
            reviewers: Specific reviewers, or auto-select
            
        Returns:
            ConsensusBuilder for tracking review progress
        """
        # Auto-select reviewers if not specified
        if not reviewers:
            reviewers = self._select_reviewers(author)
        
        # Create review request
        review_request = ReviewRequest(
            change_id=change_id,
            change_type="code",
            description=str(change),
            diff="",  # Would contain actual diff
            files_changed=[],
            author=author,
            reviewers_needed=len(reviewers),
        )
        
        # Create consensus builder
        consensus = ConsensusBuilder(
            decision_id=change_id,
            topic=f"Review: {change_id}",
            required_approvals=2,
            allow_veto=True,
        )
        
        # Send review requests
        for reviewer_name in reviewers:
            if reviewer_name in self._agents:
                message = AgentMessage(
                    sender="orchestrator",
                    receiver=reviewer_name,
                    message_type=MessageType.REVIEW,
                    content=review_request,
                    confidence=1.0,
                )
                self._agents[reviewer_name].receive_message(message)
        
        logger.info(
            "review_started",
            change_id=change_id,
            reviewers=reviewers,
        )
        
        return consensus
    
    async def handle_conflict(
        self,
        agents: list[str],
        topic: str,
        positions: dict[str, Any],
    ) -> str:
        """Handle a conflict between agents.
        
        Args:
            agents: Agents in conflict
            topic: What the conflict is about
            positions: Each agent's position
            
        Returns:
            Resolution decision
        """
        logger.info("handling_conflict", agents=agents, topic=topic)
        
        # Create consensus builder for resolution
        consensus = ConsensusBuilder(
            decision_id=f"conflict_{topic}",
            topic=topic,
            required_approvals=len(agents),
        )
        
        # Request each agent to vote on resolution
        for agent_name in agents:
            if agent_name in self._agents:
                # Ask agent to consider other positions
                agent = self._agents[agent_name]
                thought = await agent.think(
                    f"""Conflict resolution needed on: {topic}
                    
Your position: {positions.get(agent_name)}

Other positions:
{chr(10).join(f'{k}: {v}' for k, v in positions.items() if k != agent_name)}

Can you find a compromise? Vote APPROVE for compromise, REJECT to maintain position."""
                )
                
                # Add vote based on thought
                vote = Vote(
                    voter=agent_name,
                    vote_type=VoteType.APPROVE if thought.confidence > 0.6 else VoteType.REJECT,
                    confidence=thought.confidence,
                    reasoning=thought.content[:200],
                )
                consensus.add_vote(vote)
        
        result = consensus.get_result()
        
        logger.info(
            "conflict_resolved",
            topic=topic,
            approved=result.approved,
            decision=result.final_decision,
        )
        
        return result.final_decision
    
    async def run(self) -> None:
        """Run the main orchestration loop."""
        self._running = True
        logger.info("orchestrator_started")
        
        while self._running:
            try:
                # Process task queue
                try:
                    task = await asyncio.wait_for(
                        self._task_queue.get(),
                        timeout=1.0,
                    )
                    await self._process_task(task)
                except asyncio.TimeoutError:
                    pass
                
                # Process message queue
                try:
                    message = await asyncio.wait_for(
                        self._message_queue.get(),
                        timeout=0.1,
                    )
                    await self._route_message(message)
                except asyncio.TimeoutError:
                    pass
                    
            except Exception as e:
                logger.error("orchestrator_error", error=str(e))
    
    def stop(self) -> None:
        """Stop the orchestration loop."""
        self._running = False
        logger.info("orchestrator_stopped")
    
    async def _process_task(self, task: SubTask) -> None:
        """Process a task from the queue."""
        # Check dependencies
        if not self._dependencies_met(task):
            task.status = TaskStatus.BLOCKED
            await self._task_queue.put(task)  # Re-queue
            return
        
        # Assign and execute
        if await self.assign_task(task):
            task.status = TaskStatus.IN_PROGRESS
    
    async def _route_message(self, message: AgentMessage) -> None:
        """Route a message to its destination."""
        if message.receiver == "broadcast":
            for agent in self._agents.values():
                agent.receive_message(message)
        elif message.receiver in self._agents:
            self._agents[message.receiver].receive_message(message)
        else:
            logger.warning("unknown_recipient", receiver=message.receiver)
    
    def _select_agent(self, task: SubTask) -> str:
        """Select the best agent for a task."""
        # Simple capability matching (would be smarter in production)
        for name, agent in self._agents.items():
            for cap in agent.capabilities:
                if cap.lower() in task.description.lower():
                    return name
        
        # Default to first available agent
        return next(iter(self._agents.keys()), "unknown")
    
    def _select_reviewers(self, author: str, count: int = 2) -> list[str]:
        """Select reviewers for a change."""
        reviewers = []
        
        # Always include security agent if available
        for name, agent in self._agents.items():
            if name == author:
                continue
            if "security" in agent.role.lower():
                reviewers.append(name)
                break
        
        # Add other agents
        for name in self._agents:
            if name != author and name not in reviewers:
                reviewers.append(name)
                if len(reviewers) >= count:
                    break
        
        return reviewers
    
    def _dependencies_met(self, task: SubTask) -> bool:
        """Check if task dependencies are satisfied."""
        for dep_id in task.dependencies:
            # Find the dependency task
            for project in self._projects.values():
                if dep_id in project.tasks:
                    if project.tasks[dep_id].status != TaskStatus.COMPLETED:
                        return False
        return True
    
    def _parse_subtasks(self, parent_id: str, content: str) -> list[SubTask]:
        """Parse subtasks from LLM response."""
        import json
        import uuid
        
        try:
            # Try to parse as JSON
            data = json.loads(content)
            if isinstance(data, list):
                return [
                    SubTask(
                        task_id=str(uuid.uuid4())[:8],
                        parent_id=parent_id,
                        description=item.get("description", str(item)),
                        assigned_agent=item.get("agent"),
                        dependencies=item.get("dependencies", []),
                    )
                    for item in data
                ]
        except json.JSONDecodeError:
            pass
        
        # Fallback: create single subtask
        return [SubTask(
            task_id=str(uuid.uuid4())[:8],
            parent_id=parent_id,
            description=content,
        )]
