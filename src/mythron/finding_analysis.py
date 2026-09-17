"""MYTHRON — Finding analysis models.

Analyzes existing findings without performing exploitation or validation.
"""

from dataclasses import dataclass, field
from typing import List

from mythron.findings import Finding


@dataclass
class FindingAnalysis:
    """Analysis result for one security finding."""

    finding: Finding
    assessment: str
    validation_needed: bool = False
    recommended_actions: List[str] = field(default_factory=list)

    def is_actionable(self) -> bool:
        """Return True when the finding has enough evidence for follow-up."""
        return (
            self.finding.is_high_confidence()
            and bool(self.finding.evidence)
        )


class FindingAnalyzer:
    """Perform safe, evidence-based analysis of findings."""

    def analyze(self, finding: Finding) -> FindingAnalysis:
        """Analyze a finding using its existing severity and evidence."""

        validation_needed = not finding.verified

        if finding.is_high_confidence() and finding.evidence:
            assessment = (
                "Finding has strong evidence and high confidence. "
                "Controlled validation may be considered."
            )
        elif finding.evidence:
            assessment = (
                "Finding has supporting evidence but confidence is below "
                "the high-confidence threshold."
            )
        else:
            assessment = (
                "Finding has insufficient evidence for strong assessment."
            )

        return FindingAnalysis(
            finding=finding,
            assessment=assessment,
            validation_needed=validation_needed,
        )
