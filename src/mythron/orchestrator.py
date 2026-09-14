"""MYTHRON Phase 2 — Agent orchestrator with adaptive multi-path reasoning.

The AgentOrchestrator implements the agent loop:
PLAN -> FILTER -> PRIORITIZE -> SELECT -> EXECUTE -> OBSERVE -> ANALYZE ->
VERIFY -> DECIDE -> CONTINUE/STOP

When an approach fails, the orchestrator does NOT stop. It selects the
next untried approach (if any) and continues adapting until:
- objective is completed AND verified, OR
- no useful/authorized approaches remain, OR
- task reaches max_attempts stop condition

Phase 2 uses MockApproachExecutor for simulated actions. The same loop
will work with real cybersecurity executors in Phase 6+.

LLM (ReasoningCore) is optional: if None, sensible defaults are used.
This allows tests to run without making real LLM calls.
"""

import sys
from typing import List, Optional

from mythron.approaches import (
    Approach,
    AttemptHistory,
    AttemptStatus,
    AuthorizationStatus,
    ScopeStatus,
)
from mythron.executors import (
    ApproachExecutor,
    ExecutionResult,
    MockApproachExecutor,
)
from mythron.reasoning import ReasoningCore
from mythron.memory import TaskMemory
from mythron.states import StateMachine, TaskState


class AgentOrchestrator:
    """Adaptive multi-path reasoning orchestrator.

    When an approach fails, the orchestrator selects an alternative
    (if available) rather than stopping immediately.

    LLM is optional: if ReasoningCore is None, sensible defaults are used.
    """

    def __init__(
        self,
        reasoning_core: Optional[ReasoningCore] = None,
        executor: Optional[ApproachExecutor] = None,
        max_attempts: int = 10,
        memory: Optional[TaskMemory] = None,
    ) -> None:
        self._reasoning = reasoning_core
        self._executor = executor if executor is not None else MockApproachExecutor()
        self._max_attempts = max_attempts
        self._state = StateMachine()
        self._history = AttemptHistory()
        self._memory = memory
        self._objective = ""
        self._scope = ""

    @property
    def history(self) -> AttemptHistory:
        """Access the attempt history (for inspection)."""
        return self._history

    @property
    def state(self) -> TaskState:
        """Current task state."""
        return self._state.current()

    def run(
        self,
        objective: str,
        scope: str = "authorized testing only",
        approaches: Optional[List[Approach]] = None,
        resume: bool = False,
    ) -> str:
        """Run the adaptive loop. Returns 'COMPLETED' or 'STOPPED'.

        If resume=True, restore the previously persisted task before
        continuing the adaptive loop.
        """
        self._objective = objective
        self._scope = scope

        if approaches is None:
            approaches = self._generate_approaches()
        for a in approaches:
            self._history.add_approach(a)

        if resume:
            self._restore_memory()
        else:
            self._state.transition_to(TaskState.TARGET_SCOPE_DEFINED)
            self._save_memory()

        attempts = 0
        while attempts < self._max_attempts:
            next_approach = self._select_next_approach()
            if next_approach is None:
                self._state.transition_to(TaskState.STOPPED)
                return "STOPPED"

            attempt = self._execute_approach(next_approach)
            attempts += 1
            self._save_memory()

            if attempt.status == AttemptStatus.SUCCEEDED:
                if self._verify_objective():
                    self._complete_lifecycle()
                    self._save_memory()
                    return "COMPLETED"
            elif attempt.status == AttemptStatus.FAILED:
                self._analyze_failure(attempt)

        self._state.transition_to(TaskState.STOPPED)
        self._save_memory()
        return "STOPPED"

    def _complete_lifecycle(self) -> None:
        """Advance the task through valid lifecycle states to COMPLETED."""
        transitions = {
            TaskState.TASK_RECEIVED: TaskState.TARGET_SCOPE_DEFINED,
            TaskState.TARGET_SCOPE_DEFINED: TaskState.RECON,
            TaskState.RECON: TaskState.DISCOVERY,
            TaskState.DISCOVERY: TaskState.ANALYSIS,
            TaskState.ENUMERATION: TaskState.ANALYSIS,
            TaskState.ANALYSIS: TaskState.FINDINGS,
            TaskState.FINDINGS: TaskState.REPORTING,
            TaskState.REPORTING: TaskState.COMPLETED,
        }

        while self._state.current() != TaskState.COMPLETED:
            current = self._state.current()

            if current in (TaskState.STOPPED, TaskState.COMPLETED):
                return

            next_state = transitions.get(current)
            if next_state is None:
                return

            self._state.transition_to(next_state)

    def _restore_memory(self) -> None:
        """Restore persisted task metadata and completed attempts."""
        if self._memory is None:
            return

        data = self._memory.load()
        if not data:
            return

        self._objective = data.get("objective", "")
        self._scope = data.get("scope", "")

        self._restore_state(data.get("state", ""))

        for saved_attempt in data.get("attempts", []):
            approach_name = saved_attempt.get("approach")
            if not approach_name:
                continue

            approach = next(
                (
                    a
                    for a in self._history.all_approaches()
                    if a.name == approach_name
                ),
                None,
            )

            if approach is None:
                continue

            attempt = self._history.start_attempt(approach.id)

            try:
                status = AttemptStatus(saved_attempt.get("status", "FAILED"))
            except ValueError:
                status = AttemptStatus.FAILED

            self._history.complete_attempt(
                attempt_id=attempt.id,
                status=status,
                result=saved_attempt.get("result", ""),
                failure_reason=saved_attempt.get("failure_reason"),
                observations=saved_attempt.get("observations", []),
            )

    def _restore_state(self, saved_state: str) -> None:
        """Restore the persisted lifecycle state using valid transitions."""
        try:
            target = TaskState(saved_state)
        except ValueError:
            return

        if target in (TaskState.TASK_RECEIVED, TaskState.STOPPED):
            return

        state_path = [
            TaskState.TARGET_SCOPE_DEFINED,
            TaskState.RECON,
            TaskState.DISCOVERY,
            TaskState.ENUMERATION,
            TaskState.ANALYSIS,
            TaskState.FINDINGS,
            TaskState.REPORTING,
            TaskState.COMPLETED,
        ]

        if target not in state_path:
            return

        target_index = state_path.index(target)

        for next_state in state_path[:target_index + 1]:
            if self._state.can_transition_to(next_state):
                self._state.transition_to(next_state)
            elif self._state.current() == next_state:
                continue
            else:
                break

    def _save_memory(self) -> None:
        """Persist the current task state and attempt history."""
        if self._memory is None:
            return

        attempts = []
        for attempt in self._history.all_attempts():
            approach = self._history.get_approach(attempt.approach_id)
            attempts.append(
                {
                    "id": attempt.id,
                    "approach": approach.name if approach else "unknown",
                    "status": attempt.status.value,
                    "result": attempt.result,
                    "failure_reason": attempt.failure_reason,
                    "observations": list(attempt.observations),
                }
            )

        data = {
            "objective": self._objective,
            "scope": self._scope,
            "state": self.state.value,
            "attempts": attempts,
        }

        self._memory.save(data)

    def _generate_approaches(self) -> List[Approach]:
        """Generate approaches. LLM if available, else defaults."""
        if self._reasoning is None:
            return self._default_approaches()
        # Phase 2: LLM-based generation deferred to later phase.
        # For now, use defaults even when LLM is available.
        return self._default_approaches()

    def _default_approaches(self) -> List[Approach]:
        """Hardcoded default approaches for Phase 2 testing."""
        return [
            Approach(
                name="recon_port_scan",
                description="Scan for open ports on the target",
                relevance=0.9,
                authorization=AuthorizationStatus.AUTHORIZED,
                scope=ScopeStatus.IN_SCOPE,
                expected_value=0.8,
            ),
            Approach(
                name="dns_lookup",
                description="DNS reconnaissance for the target domain",
                relevance=0.7,
                authorization=AuthorizationStatus.AUTHORIZED,
                scope=ScopeStatus.IN_SCOPE,
                expected_value=0.5,
            ),
            Approach(
                name="web_crawl",
                description="Crawl public web pages of the target",
                relevance=0.8,
                authorization=AuthorizationStatus.AUTHORIZED,
                scope=ScopeStatus.IN_SCOPE,
                expected_value=0.6,
            ),
        ]

    def _select_next_approach(self) -> Optional[Approach]:
        """Select highest-priority untried approach. None if no untried remain."""
        untried = self._history.untried_approaches()
        if not untried:
            return None
        untried.sort(key=lambda a: a.priority(), reverse=True)
        return untried[0]

    def _execute_approach(self, approach: Approach):
        """Execute via executor, record in history, return updated Attempt."""
        attempt = self._history.start_attempt(approach.id)
        result = self._executor.execute(approach)
        self._history.complete_attempt(
            attempt_id=attempt.id,
            status=result.status,
            result=result.result,
            failure_reason=result.failure_reason if result.failure_reason else None,
            observations=result.observations,
        )
        return self._history.all_attempts()[-1]

    def _analyze_failure(self, attempt) -> str:
        """Analyze why the attempt failed. Use LLM if available."""
        approach = self._history.get_approach(attempt.approach_id)
        name = approach.name if approach else "unknown"
        if self._reasoning is None:
            return f"Failure recorded for {name}. No LLM analysis available."
        prompt = (
            f"You are MYTHRON, a cybersecurity AI analyzing a failed approach.\n"
            f"Objective: {self._objective}\n"
            f"Approach: {name}\n"
            f"Failure reason: {attempt.failure_reason}\n"
            f"Observations: {', '.join(attempt.observations)}\n\n"
            f"In one or two sentences, explain the root cause."
        )
        try:
            return self._reasoning.reason(prompt)
        except Exception as exc:
            return f"LLM analysis failed: {exc}"

    def _verify_objective(self) -> bool:
        """Phase 2 heuristic: objective met if >=1 attempt succeeded."""
        return len(self._history.approaches_succeeded()) > 0


def main() -> int:
    """CLI demo: run orchestrator with mock approaches (no LLM)."""
    print("=== MYTHRON Orchestrator — demo (mock, no LLM) ===")

    # Configure mock executor: "recon_port_scan" will fail, others will succeed
    executor = MockApproachExecutor(fail_names={"recon_port_scan"})

    orchestrator = AgentOrchestrator(
        reasoning_core=None,  # no LLM for Phase 2 demo
        executor=executor,
        max_attempts=10,
    )

    print("\nObjective: Assess authorized target example.com")
    print("Scope: authorized testing only")
    print("Executor: mock (recon_port_scan will FAIL, others SUCCEED)")
    print()

    status = orchestrator.run(
        objective="Assess authorized target example.com",
        scope="authorized testing only",
    )

    print(f"\nFinal status: {status}")
    print(f"Final state: {orchestrator.state.value}")
    print(f"\n{orchestrator.history.summary()}")
    print(f"Attempts made: {len(orchestrator.history.all_attempts())}")
    print(f"Approaches tried: {orchestrator.history.approaches_tried()}")
    print(f"Approaches succeeded: {orchestrator.history.approaches_succeeded()}")
    print(f"Approaches failed: {orchestrator.history.approaches_failed()}")
    print(f"Untried approaches: {[a.name for a in orchestrator.history.untried_approaches()]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
