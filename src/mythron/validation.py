"""MYTHRON Phase 7 — Controlled validation workflow.

Validation requires explicit approval before execution can begin.
This module does not perform exploitation or active security actions.
"""

from dataclasses import dataclass, field
from enum import Enum

from mythron.findings import Finding


class ValidationStatus(Enum):
    """Lifecycle status of a validation request."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"


class ValidationOutcome(Enum):
    """Outcome of a controlled validation attempt."""

    CONFIRMED = "CONFIRMED"
    NOT_CONFIRMED = "NOT_CONFIRMED"
    FAILED = "FAILED"


@dataclass
class ValidationResult:
    """Structured result returned by a controlled validation attempt."""

    outcome: ValidationOutcome
    summary: str = ""
    evidence: list[str] = field(default_factory=list)


@dataclass
class ValidationRequest:
    """A controlled validation request for one finding."""

    finding: Finding
    category: str = "generic"
    status: ValidationStatus = ValidationStatus.PENDING
    approved: bool = False

    def approve(self) -> None:
        """Explicitly approve the validation request."""
        if self.status != ValidationStatus.PENDING:
            raise ValueError("Only pending validation requests can be approved.")

        self.approved = True
        self.finding.request_validation()

    def reject(self) -> None:
        """Reject the validation request."""
        if self.status != ValidationStatus.PENDING:
            raise ValueError("Only pending validation requests can be rejected.")

        self.approved = False
        self.status = ValidationStatus.REJECTED

    def start(self) -> None:
        """Start validation only after explicit approval."""
        if not self.approved:
            raise PermissionError(
                "Validation requires explicit approval."
            )

        if self.status != ValidationStatus.PENDING:
            raise ValueError(
                "Only pending validation requests can be started."
            )

        self.status = ValidationStatus.IN_PROGRESS

    def complete(self) -> None:
        """Complete an active validation request."""
        if self.status != ValidationStatus.IN_PROGRESS:
            raise ValueError(
                "Validation must be in progress before completion."
            )

        self.status = ValidationStatus.COMPLETED
        self.finding.mark_verified()
