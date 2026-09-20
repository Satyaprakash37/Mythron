"""MYTHRON Phase 11 — UI assessment controller.

Thin application layer between the desktop UI and AssessmentEngine.
Security authorization remains enforced by the assessment domain/engine.
"""

from mythron.approaches import (
    Approach,
    AuthorizationStatus,
    ScopeStatus,
)
from mythron.assessment import AssessmentStatus
from mythron.assessment_engine import (
    AssessmentEngine,
    AssessmentExecution,
)


class AssessmentController:
    """Coordinate UI actions with the controlled assessment engine."""

    def __init__(self, engine: AssessmentEngine) -> None:
        self._engine = engine

    @property
    def assessment(self):
        """Return the controlled assessment."""
        return self._engine._assessment

    @property
    def target(self) -> str:
        """Return the configured assessment target."""
        return self.assessment.scope.target

    @property
    def status(self) -> AssessmentStatus:
        """Return the current assessment lifecycle status."""
        return self.assessment.status

    def start(self) -> None:
        """Start the assessment through its authorization boundary."""
        self.assessment.start()

    def execute(
        self,
        capability_name: str,
        approach_name: str,
        target: str,
    ) -> AssessmentExecution:
        """Execute one explicitly scoped approach through AssessmentEngine."""

        approach = Approach(
            name=approach_name,
            description=target,
            relevance=1.0,
            authorization=AuthorizationStatus.AUTHORIZED,
            scope=ScopeStatus.IN_SCOPE,
            expected_value=1.0,
        )

        return self._engine.execute(
            capability_name=capability_name,
            approach=approach,
        )
