"""MYTHRON Phase 6 — Security finding models.

Findings record potential or confirmed security issues.
This module does not execute validation or exploitation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Severity(Enum):
    """Finding severity."""

    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class Finding:
    """A security finding discovered during an assessment."""

    title: str
    description: str
    target: str
    severity: Severity = Severity.INFO
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    verified: bool = False
    validation_requested: bool = False

    def request_validation(self) -> None:
        """Mark this finding as awaiting human validation approval."""
        self.validation_requested = True

    def mark_verified(self) -> None:
        """Mark the finding as verified after controlled validation."""
        self.verified = True

    def add_evidence(self, item: str) -> None:
        """Add an evidence item to the finding."""
        if item.strip():
            self.evidence.append(item)

    def is_high_confidence(self) -> bool:
        """Return True when confidence meets the high-confidence threshold."""
        return self.confidence >= 0.8
