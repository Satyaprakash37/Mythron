"""MYTHRON Phase 7 — Security assessment reporting.

Builds a structured report from existing findings and collected evidence.
This module does not perform active security actions.
"""

from dataclasses import dataclass
from typing import List

from mythron.evidence import EvidenceCollector
from mythron.findings import Finding, FindingStore


@dataclass
class ReportFinding:
    """Report-safe representation of one finding."""

    title: str
    description: str
    target: str
    severity: str
    confidence: float
    verified: bool
    evidence: List[str]


@dataclass
class AssessmentReport:
    """Structured security assessment report."""

    total_findings: int
    findings: List[ReportFinding]

    def summary(self) -> dict:
        """Return a severity summary for the report."""
        summary = {"total": self.total_findings}

        for item in self.findings:
            summary[item.severity] = summary.get(item.severity, 0) + 1

        return summary


class ReportGenerator:
    """Generate a report from stored assessment findings."""

    def __init__(
        self,
        evidence_collector: EvidenceCollector | None = None,
    ) -> None:
        self._evidence_collector = evidence_collector or EvidenceCollector()

    def generate(self, store: FindingStore) -> AssessmentReport:
        """Generate a structured report from the finding store."""
        report_findings = [
            self._build_finding(finding)
            for finding in store.all()
        ]

        return AssessmentReport(
            total_findings=len(report_findings),
            findings=report_findings,
        )

    def _build_finding(self, finding: Finding) -> ReportFinding:
        return ReportFinding(
            title=finding.title,
            description=finding.description,
            target=finding.target,
            severity=finding.severity.value,
            confidence=finding.confidence,
            verified=finding.verified,
            evidence=self._evidence_collector.collect(finding),
        )
