"""MYTHRON Phase 2 — State machine for the agent orchestrator.

Defines the 13 task-level states from ARCHITECTURE.md and the valid
transitions between them. The adaptive loop (plan/act/observe/analyze/
verify/decide/stop) operates WITHIN each task state — it does not
change the task state directly.

This module is intentionally small and side-effect-free so it can be
unit tested without any LLM or external dependencies.
"""

from enum import Enum
from typing import Dict, List, Set, Tuple


class TaskState(Enum):
    """Task lifecycle states (from ARCHITECTURE.md)."""

    TASK_RECEIVED = "TASK_RECEIVED"
    TARGET_SCOPE_DEFINED = "TARGET_SCOPE_DEFINED"
    RECON = "RECON"
    DISCOVERY = "DISCOVERY"
    ENUMERATION = "ENUMERATION"
    ANALYSIS = "ANALYSIS"
    FINDINGS = "FINDINGS"
    VALIDATION_REQUESTED = "VALIDATION_REQUESTED"
    VALIDATING = "VALIDATING"
    EVIDENCE_COLLECTION = "EVIDENCE_COLLECTION"
    REPORTING = "REPORTING"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"


# Valid state transitions.
# Each state maps to the set of states it can transition to.
# The orchestrator may move forward through the normal lifecycle,
# or jump to STOPPED from any state (emergency stop).
# COMPLETED and STOPPED are terminal — no outgoing transitions.
VALID_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.TASK_RECEIVED: {TaskState.TARGET_SCOPE_DEFINED, TaskState.STOPPED},
    TaskState.TARGET_SCOPE_DEFINED: {TaskState.RECON, TaskState.STOPPED},
    TaskState.RECON: {TaskState.DISCOVERY, TaskState.STOPPED},
    TaskState.DISCOVERY: {TaskState.ENUMERATION, TaskState.ANALYSIS, TaskState.STOPPED},
    TaskState.ENUMERATION: {TaskState.ANALYSIS, TaskState.STOPPED},
    TaskState.ANALYSIS: {TaskState.FINDINGS, TaskState.DISCOVERY, TaskState.STOPPED},
    TaskState.FINDINGS: {TaskState.VALIDATION_REQUESTED, TaskState.REPORTING, TaskState.STOPPED},
    TaskState.VALIDATION_REQUESTED: {TaskState.VALIDATING, TaskState.STOPPED},
    TaskState.VALIDATING: {TaskState.EVIDENCE_COLLECTION, TaskState.FINDINGS, TaskState.STOPPED},
    TaskState.EVIDENCE_COLLECTION: {TaskState.REPORTING, TaskState.STOPPED},
    TaskState.REPORTING: {TaskState.COMPLETED, TaskState.STOPPED},
    TaskState.COMPLETED: set(),
    TaskState.STOPPED: set(),
}


class StateMachineError(Exception):
    """Raised when an invalid state transition is attempted."""


class StateMachine:
    """Tracks the current state of an agent task.

    Validates transitions against VALID_TRANSITIONS.
    Records history of transitions for debugging and audit.
    """

    def __init__(self, initial: TaskState = TaskState.TASK_RECEIVED) -> None:
        self._current = initial
        self._history: List[Tuple[TaskState, TaskState]] = []

    def current(self) -> TaskState:
        """Return the current state."""
        return self._current

    def can_transition_to(self, new_state: TaskState) -> bool:
        """Check whether transitioning to new_state is valid."""
        return new_state in VALID_TRANSITIONS.get(self._current, set())

    def transition_to(self, new_state: TaskState) -> None:
        """Transition to new_state. Raises StateMachineError if invalid."""
        if not self.can_transition_to(new_state):
            raise StateMachineError(
                f"Invalid transition: {self._current.value} -> {new_state.value}"
            )
        old_state = self._current
        self._current = new_state
        self._history.append((old_state, new_state))

    def history(self) -> List[Tuple[TaskState, TaskState]]:
        """Return transition history as (from, to) tuples."""
        return list(self._history)

    def is_terminal(self) -> bool:
        """True if current state is terminal (COMPLETED or STOPPED)."""
        return self._current in (TaskState.COMPLETED, TaskState.STOPPED)


def main() -> int:
    """CLI demo: walk through a happy-path state sequence."""
    print("=== MYTHRON State Machine — demo ===")
    sm = StateMachine()
    print(f"Initial state: {sm.current().value}")

    sequence = [
        TaskState.TARGET_SCOPE_DEFINED,
        TaskState.RECON,
        TaskState.DISCOVERY,
        TaskState.ENUMERATION,
        TaskState.ANALYSIS,
        TaskState.FINDINGS,
        TaskState.REPORTING,
        TaskState.COMPLETED,
    ]

    for next_state in sequence:
        sm.transition_to(next_state)
        print(f"  -> {sm.current().value}")

    print()
    print(f"Final state: {sm.current().value}")
    print(f"Terminal: {sm.is_terminal()}")
    print(f"History ({len(sm.history())} transitions):")
    for i, (old, new) in enumerate(sm.history(), 1):
        print(f"  [{i}] {old.value} -> {new.value}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
