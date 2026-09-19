"""MYTHRON Phase 2 — Approach executors.

Defines the ApproachExecutor protocol (interface) that all approach
executors must implement. Phase 2 ships MockApproachExecutor for
simulated actions. Phase 6+ will add real executors (browser, dynamic
code, security tools) that implement the same interface.

This separation ensures the adaptive reasoning loop is capability-agnostic:
the orchestrator works the same way whether the executor is mocked or real.
"""

from dataclasses import dataclass, field
from typing import List, Protocol, Set, runtime_checkable

from mythron.approaches import (
    AttemptStatus,
    Approach,
)


@dataclass
class ExecutionResult:
    """Result of executing an approach.

    The orchestrator takes this and records it via AttemptHistory.complete_attempt.
    """
    status: AttemptStatus
    result: str = ""
    failure_reason: str = ""
    observations: List[str] = field(default_factory=list)
    data: object | None = None


@runtime_checkable
class ApproachExecutor(Protocol):
    """Interface for executing an approach.

    All executors (mock or real) must implement this. The orchestrator
    uses this interface without caring about the underlying implementation.

    The runtime_checkable decorator allows isinstance() checks against
    the protocol (e.g., isinstance(executor, ApproachExecutor)).
    """

    @property
    def name(self) -> str:
        """Executor name (e.g., 'mock', 'browser', 'dynamic_code')."""
        ...

    def can_execute(self, approach: Approach) -> bool:
        """Return True if this executor can handle the given approach."""
        ...

    def execute(self, approach: Approach) -> ExecutionResult:
        """Execute the approach and return the result."""
        ...


class MockApproachExecutor:
    """Mock executor for Phase 2 simulated actions.

    By default, all approaches succeed. Configure `fail_names` to make
    specific approaches fail (useful for testing the adaptive loop).
    """

    def __init__(
        self,
        fail_names: Set[str] = None,
        success_result: str = "Mock execution succeeded",
        failure_result: str = "Mock execution failed",
        failure_reason: str = "Approach configured to fail",
    ) -> None:
        self._fail_names = fail_names if fail_names is not None else set()
        self._success_result = success_result
        self._failure_result = failure_result
        self._failure_reason = failure_reason

    @property
    def name(self) -> str:
        return "mock"

    def can_execute(self, approach: Approach) -> bool:
        """Mock executor can handle any approach."""
        return True

    def execute(self, approach: Approach) -> ExecutionResult:
        """Execute the approach. Fails if approach.name is in fail_names."""
        if approach.name in self._fail_names:
            return ExecutionResult(
                status=AttemptStatus.FAILED,
                result=self._failure_result,
                failure_reason=self._failure_reason,
                observations=[f"Mock failed for: {approach.name}"],
            )
        return ExecutionResult(
            status=AttemptStatus.SUCCEEDED,
            result=self._success_result,
            observations=[f"Mock succeeded for: {approach.name}"],
        )


def main() -> int:
    """CLI demo: exercise MockApproachExecutor."""
    print("=== MYTHRON Executors — demo ===")

    a1 = Approach(name="http_port_scan", description="HTTP port scan", relevance=0.9)
    a2 = Approach(name="ssh_brute", description="SSH brute force", relevance=0.4)

    # Default mock - all succeed
    exec1 = MockApproachExecutor()
    r1 = exec1.execute(a1)
    print(f"Default mock, exec({a1.name}): {r1.status.value}")
    print(f"  result: {r1.result}")
    print(f"  observations: {r1.observations}")

    # Configured mock - ssh_brute fails
    exec2 = MockApproachExecutor(fail_names={"ssh_brute"})
    r2 = exec2.execute(a2)
    print(f"\nConfigured mock, exec({a2.name}): {r2.status.value}")
    print(f"  result: {r2.result}")
    print(f"  failure_reason: {r2.failure_reason}")
    print(f"  observations: {r2.observations}")

    # Test can_execute
    print(f"\ncan_execute(a1) = {exec1.can_execute(a1)}")
    print(f"can_execute(a2) = {exec1.can_execute(a2)}")

    # Verify protocol compliance
    print(f"\nisinstance(exec1, ApproachExecutor) = {isinstance(exec1, ApproachExecutor)}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
