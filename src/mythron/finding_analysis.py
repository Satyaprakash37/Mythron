"""MYTHRON — Finding analysis models.

Analyzes existing findings without performing exploitation or validation.
"""

from dataclasses import dataclass, field
from typing import List

from mythron.findings import Finding


@dataclass
class ValidationPlan:
    """A controlled, non-executing plan for validating a finding."""

    objective: str
    method: str
    category: str = "generic"
    evidence_to_collect: List[str] = field(default_factory=list)
    requires_explicit_approval: bool = True


@dataclass
class FindingAnalysis:
    """Analysis result for one security finding."""

    finding: Finding
    assessment: str
    validation_needed: bool = False
    recommended_actions: List[str] = field(default_factory=list)
    validation_plan: ValidationPlan | None = None

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

        validation_plan = None

        if (
            validation_needed
            and finding.is_high_confidence()
            and finding.evidence
        ):
            if finding.title == "Missing Content-Security-Policy Header":
                validation_plan = ValidationPlan(
                    objective=(
                        "Confirm whether the authorized target response "
                        "consistently omits the Content-Security-Policy header."
                    ),
                    method=(
                        "Perform a controlled HTTP response-header check "
                        "against the authorized target and compare the "
                        "observed headers with the discovery evidence."
                    ),
                    category="http_response_header",
                    evidence_to_collect=[
                        "Validation request and approval state",
                        "Observed Content-Security-Policy header state",
                        "Response evidence showing whether the condition "
                        "is reproducible",
                    ],
                )
            else:
                validation_plan = ValidationPlan(
                    objective=f"Validate whether the observed condition for "
                    f"{finding.title!r} is reproducible.",
                    method=(
                        "Perform a controlled, non-destructive check against "
                        "the authorized assessment target and compare the "
                        "result with the existing evidence."
                    ),
                    category="generic",
                    evidence_to_collect=[
                        "Validation request and approval state",
                        "Observed response or application behavior",
                        "Evidence showing whether the finding was confirmed",
                    ],
                )

        return FindingAnalysis(
            finding=finding,
            assessment=assessment,
            validation_needed=validation_needed,
            validation_plan=validation_plan,
        )
