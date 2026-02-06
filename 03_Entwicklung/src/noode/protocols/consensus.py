"""Consensus building protocol for multi-agent decisions."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger()


class VoteType(Enum):
    """Types of votes an agent can cast."""
    
    APPROVE = "approve"
    REJECT = "reject"
    ABSTAIN = "abstain"
    REQUEST_CHANGES = "request_changes"


@dataclass
class Vote:
    """A vote from an agent on a decision."""
    
    voter: str
    vote_type: VoteType
    confidence: float
    reasoning: str
    concerns: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ConsensusResult:
    """Result of a consensus-building process."""
    
    decision_id: str
    approved: bool
    votes: list[Vote]
    final_decision: str
    dissenting_opinions: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)


class ConsensusBuilder:
    """Builds consensus among multiple agents.
    
    Implements a weighted voting system where:
    - Security agents have veto power on security matters
    - Vote weight is adjusted by agent confidence
    - Minimum approval threshold must be met
    
    Attributes:
        decision_id: Unique identifier for the decision
        topic: What is being decided
        required_approvals: Minimum approvals needed
        allow_veto: Whether any agent can veto
    """
    
    def __init__(
        self,
        decision_id: str,
        topic: str,
        required_approvals: int = 2,
        allow_veto: bool = True,
    ) -> None:
        """Initialize consensus builder.
        
        Args:
            decision_id: Unique ID for this decision
            topic: Description of what's being decided
            required_approvals: Minimum number of approvals
            allow_veto: Whether vetoes are allowed
        """
        self.decision_id = decision_id
        self.topic = topic
        self.required_approvals = required_approvals
        self.allow_veto = allow_veto
        self._votes: list[Vote] = []
        self._vetoed = False
        self._veto_reason: str | None = None
    
    def add_vote(self, vote: Vote) -> None:
        """Add a vote to the consensus.
        
        Args:
            vote: The vote to add
        """
        # Check for duplicate votes
        for existing in self._votes:
            if existing.voter == vote.voter:
                logger.warning(
                    "duplicate_vote",
                    voter=vote.voter,
                    decision=self.decision_id,
                )
                return
        
        self._votes.append(vote)
        
        # Check for veto
        if self.allow_veto and vote.vote_type == VoteType.REJECT:
            if "security" in vote.voter.lower() and vote.concerns:
                self._vetoed = True
                self._veto_reason = f"Security veto: {vote.concerns[0]}"
                logger.warning(
                    "decision_vetoed",
                    voter=vote.voter,
                    reason=self._veto_reason,
                )
        
        logger.info(
            "vote_recorded",
            decision=self.decision_id,
            voter=vote.voter,
            vote=vote.vote_type.value,
            confidence=vote.confidence,
        )
    
    def get_result(self) -> ConsensusResult:
        """Calculate and return the consensus result.
        
        Returns:
            ConsensusResult with the final decision
        """
        if self._vetoed:
            return ConsensusResult(
                decision_id=self.decision_id,
                approved=False,
                votes=self._votes,
                final_decision=self._veto_reason or "Vetoed",
                dissenting_opinions=[
                    v.reasoning for v in self._votes 
                    if v.vote_type in (VoteType.REJECT, VoteType.REQUEST_CHANGES)
                ],
            )
        
        # Count weighted approvals
        approvals = sum(
            v.confidence for v in self._votes 
            if v.vote_type == VoteType.APPROVE
        )
        
        rejections = sum(
            v.confidence for v in self._votes
            if v.vote_type == VoteType.REJECT
        )
        
        approved = approvals >= self.required_approvals and approvals > rejections
        
        # Collect conditions from REQUEST_CHANGES votes
        conditions = []
        for vote in self._votes:
            if vote.vote_type == VoteType.REQUEST_CHANGES:
                conditions.extend(vote.concerns)
        
        return ConsensusResult(
            decision_id=self.decision_id,
            approved=approved,
            votes=self._votes,
            final_decision="Approved" if approved else "Rejected",
            dissenting_opinions=[
                v.reasoning for v in self._votes
                if v.vote_type == VoteType.REJECT
            ],
            conditions=conditions,
        )
    
    @property
    def is_complete(self) -> bool:
        """Check if enough votes have been collected.
        
        Returns:
            True if we have enough votes to decide
        """
        if self._vetoed:
            return True
        return len(self._votes) >= self.required_approvals
    
    @property
    def pending_count(self) -> int:
        """Number of votes still needed.
        
        Returns:
            Count of additional votes needed
        """
        return max(0, self.required_approvals - len(self._votes))
