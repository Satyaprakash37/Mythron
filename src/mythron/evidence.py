"""MYTHRON Phase 7 — Evidence collection.

Collects existing evidence from findings without performing active
security actions or modifying the finding.
"""

from typing import List

from mythron.findings import Finding


class EvidenceCollector:
    """Collect clean evidence items from a security finding."""

    def collect(self, finding: Finding) -> List[str]:
        """Return non-empty evidence items without modifying the finding."""
        return [
            item
            for item in finding.evidence
            if item.strip()
        ]
