"""MYTHRON Phase 6 — Assessment scope and lifecycle models.

This module defines the safe boundary for a security assessment.
It does not execute security actions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class AssessmentStatus(Enum):
    """Lifecycle status of an assessment."""

    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


@dataclass
class AssessmentScope:
    """Explicit authorization boundary for an assessment."""

    target: str
    authorized: bool = False
    allowed_capabilities: List[str] = field(default_factory=list)

    def allows_capability(self, capability_name: str) -> bool:
        """Return True when the capability is explicitly allowed."""
        return (
            self.authorized
            and capability_name in self.allowed_capabilities
        )

    def allows_target(self, target: str) -> bool:
        """Return True when the target exactly matches the assessment target."""
        return self.authorized and target.strip() == self.target.strip()


@dataclass
class Assessment:
    """Represents one controlled security assessment."""

    name: str
    scope: AssessmentScope
    status: AssessmentStatus = AssessmentStatus.CREATED
    findings_count: int = 0

    def start(self) -> None:
        """Start the assessment only when authorization exists."""
        if not self.scope.authorized:
            raise PermissionError(
                "Assessment cannot start without explicit authorization."
            )

        self.status = AssessmentStatus.ACTIVE

    def pause(self) -> None:
        """Pause an active assessment."""
        if self.status == AssessmentStatus.ACTIVE:
            self.status = AssessmentStatus.PAUSED

    def complete(self) -> None:
        """Mark the assessment as completed."""
        self.status = AssessmentStatus.COMPLETED

    def stop(self) -> None:
        """Stop the assessment."""
        self.status = AssessmentStatus.STOPPED

    def can_use_capability(self, capability_name: str) -> bool:
        """Check whether a capability is allowed by this assessment."""
        return (
            self.status == AssessmentStatus.ACTIVE
            and self.scope.allows_capability(capability_name)
        )
