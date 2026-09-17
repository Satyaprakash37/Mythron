"""MYTHRON — Passive security signal detection.

This module analyzes already-captured browser observations.
It does not exploit, modify, or actively attack the target.
"""

from typing import List

from mythron.browser import BrowserObservation
from mythron.findings import Finding, Severity


class SecuritySignalDetector:
    """Detect passive security signals from browser observations."""

    def analyze(self, observation: BrowserObservation) -> List[Finding]:
        """Analyze response metadata and return evidence-backed findings."""
        findings: List[Finding] = []

        if not observation.has_header("content-security-policy"):
            findings.append(
                Finding(
                    title="Missing Content-Security-Policy Header",
                    description=(
                        "The observed HTTP response does not include a "
                        "Content-Security-Policy response header."
                    ),
                    target=observation.url,
                    severity=Severity.LOW,
                    confidence=1.0,
                    evidence=[
                        "Observed response header set does not contain "
                        "content-security-policy."
                    ],
                )
            )

        if (
            observation.url.lower().startswith("https://")
            and not observation.has_header("strict-transport-security")
        ):
            findings.append(
                Finding(
                    title="Missing Strict-Transport-Security Header",
                    description=(
                        "The observed HTTPS response does not include a "
                        "Strict-Transport-Security response header."
                    ),
                    target=observation.url,
                    severity=Severity.LOW,
                    confidence=1.0,
                    evidence=[
                        "Observed HTTPS response header set does not contain "
                        "strict-transport-security."
                    ],
                )
            )

        return findings
