"""MYTHRON — Controlled discovery models and engine.

Discovery collects and normalizes observations from an authorized
assessment. It does not validate or exploit vulnerabilities.
"""

from dataclasses import dataclass, field
from typing import List

from mythron.browser import BrowserObservation


@dataclass
class DiscoveryResult:
    """Normalized discovery information for one observed page."""

    target: str
    title: str
    text: str
    links: List[str] = field(default_factory=list)
    forms: List[str] = field(default_factory=list)


class DiscoveryEngine:
    """Collect structured observations from controlled browser inspection."""

    def __init__(self) -> None:
        """Initialize an empty discovery inventory."""
        self._results: List[DiscoveryResult] = []

    def record(self, observation: BrowserObservation) -> DiscoveryResult:
        """Convert and store a browser observation."""

        links = list(dict.fromkeys(
            link.strip()
            for link in observation.links
            if link and link.strip()
        ))

        forms = list(dict.fromkeys(
            form.strip()
            for form in observation.forms
            if form and form.strip()
        ))

        result = DiscoveryResult(
            target=observation.url,
            title=observation.title,
            text=observation.text,
            links=links,
            forms=forms,
        )

        self._results.append(result)
        return result

    def results(self) -> List[DiscoveryResult]:
        """Return all recorded discovery results."""
        return list(self._results)

    def summary(self) -> dict:
        """Return aggregate statistics for the discovery inventory."""
        unique_links = set()
        unique_forms = set()

        for result in self._results:
            unique_links.update(result.links)
            unique_forms.update(result.forms)

        return {
            "pages": len(self._results),
            "unique_links": len(unique_links),
            "unique_forms": len(unique_forms),
        }
