"""MYTHRON Phase 6 — Controlled assessment engine.

Connects assessment scope, capabilities, approaches, and executors.
This engine does not perform exploitation.
"""

from dataclasses import dataclass
from typing import Dict

from mythron.approaches import (
    Approach,
    AuthorizationStatus,
    ScopeStatus,
)
from mythron.assessment import Assessment
from mythron.capabilities import CapabilityRegistry
from mythron.executors import ApproachExecutor, ExecutionResult


@dataclass
class AssessmentExecution:
    """Result of a controlled assessment execution."""

    allowed: bool
    result: ExecutionResult | None = None
    reason: str = ""


class AssessmentEngine:
    """Coordinate authorized assessment capabilities."""

    def __init__(
        self,
        assessment: Assessment,
        capabilities: CapabilityRegistry,
        executors: Dict[str, ApproachExecutor],
    ) -> None:
        self._assessment = assessment
        self._capabilities = capabilities
        self._executors = executors

    def execute(self, capability_name: str, approach: Approach) -> AssessmentExecution:
        """Execute an approach only when all control checks pass."""

        if not self._assessment.scope.authorized:
            return AssessmentExecution(
                allowed=False,
                reason="Assessment scope is not authorized.",
            )

        if not self._assessment.can_use_capability(capability_name):
            return AssessmentExecution(
                allowed=False,
                reason=f"Capability is not allowed: {capability_name}",
            )

        capability = self._capabilities.get(capability_name)

        if capability is None:
            return AssessmentExecution(
                allowed=False,
                reason=f"Capability is not registered: {capability_name}",
            )

        if not capability.enabled:
            return AssessmentExecution(
                allowed=False,
                reason=f"Capability is disabled: {capability_name}",
            )

        if (
            approach.authorization != AuthorizationStatus.AUTHORIZED
            or approach.scope != ScopeStatus.IN_SCOPE
        ):
            return AssessmentExecution(
                allowed=False,
                reason="Approach is not explicitly authorized and in scope.",
            )

        executor = self._executors.get(capability_name)

        if executor is None:
            return AssessmentExecution(
                allowed=False,
                reason=f"No executor registered for: {capability_name}",
            )

        if not executor.can_execute(approach):
            return AssessmentExecution(
                allowed=False,
                reason=f"Executor cannot execute: {approach.name}",
            )

        result = executor.execute(approach)

        return AssessmentExecution(
            allowed=True,
            result=result,
        )
