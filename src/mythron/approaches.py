"""MYTHRON Phase 2 — Approach/Attempt/AttemptHistory data structures.

Tracks:
- What approaches are available (Approach)
- Which approaches have been tried (AttemptHistory.approaches_tried)
- What happened in each attempt (Attempt)
- Why approaches failed (Attempt.failure_reason)
- What alternatives remain (AttemptHistory.untried_approaches)
- Which approach is currently in progress (AttemptHistory.current_attempt)

This module is side-effect-free (no LLM, no I/O) so it can be unit tested
in isolation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class AuthorizationStatus(Enum):
    """Whether an approach is within the authorized scope."""
    AUTHORIZED = "AUTHORIZED"
    UNAUTHORIZED = "UNAUTHORIZED"
    UNKNOWN = "UNKNOWN"


class ScopeStatus(Enum):
    """Whether an approach is within the target boundaries."""
    IN_SCOPE = "IN_SCOPE"
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    UNKNOWN = "UNKNOWN"


class AttemptStatus(Enum):
    """Lifecycle status of a single attempt."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"


@dataclass
class Approach:
    """A candidate approach for the agent to try.

    priority() combines relevance, authorization, scope, and expected_value.
    Approaches that are UNAUTHORIZED or OUT_OF_SCOPE get priority 0.
    """
    name: str
    description: str
    relevance: float = 0.0
    authorization: AuthorizationStatus = AuthorizationStatus.UNKNOWN
    scope: ScopeStatus = ScopeStatus.UNKNOWN
    expected_value: float = 0.0
    id: Optional[int] = None

    def priority(self) -> float:
        """Higher = more preferred. 0 if unauthorized or out of scope."""
        if self.authorization == AuthorizationStatus.UNAUTHORIZED:
            return 0.0
        if self.scope == ScopeStatus.OUT_OF_SCOPE:
            return 0.0
        return self.relevance * self.expected_value


@dataclass
class Attempt:
    """A single execution of an approach.

    status: PENDING/IN_PROGRESS/SUCCEEDED/FAILED/SKIPPED.
    failure_reason: only set when status=FAILED.
    observations: free-form list of observation strings.
    """
    approach_id: int
    status: AttemptStatus = AttemptStatus.PENDING
    result: str = ""
    failure_reason: Optional[str] = None
    observations: List[str] = field(default_factory=list)
    id: Optional[int] = None


class AttemptHistory:
    """Tracks all known approaches and all attempts made.

    Provides queries:
    - approaches_tried(): IDs of approaches that have an attempt
    - approaches_succeeded(): IDs of approaches with at least one SUCCEEDED
    - approaches_failed(): IDs of approaches where ALL attempts FAILED
    - untried_approaches(): approaches with no attempt yet
    - current_attempt(): the in-progress attempt, if any
    """

    def __init__(self) -> None:
        self._approaches: Dict[int, Approach] = {}
        self._attempts: Dict[int, Attempt] = {}
        self._next_approach_id = 1
        self._next_attempt_id = 1
        self._current_attempt_id: Optional[int] = None

    def add_approach(self, approach: Approach) -> Approach:
        """Add an approach, auto-assign ID, return updated approach."""
        approach.id = self._next_approach_id
        self._next_approach_id += 1
        self._approaches[approach.id] = approach
        return approach

    def get_approach(self, approach_id: int) -> Optional[Approach]:
        """Get an approach by ID."""
        return self._approaches.get(approach_id)

    def all_approaches(self) -> List[Approach]:
        """Return all known approaches."""
        return list(self._approaches.values())



    def start_attempt(self, approach_id: int) -> Attempt:
        """Start a new attempt for the given approach."""
        attempt = Attempt(
            approach_id=approach_id,
            status=AttemptStatus.IN_PROGRESS,
            id=self._next_attempt_id,
        )
        self._next_attempt_id += 1
        self._attempts[attempt.id] = attempt
        self._current_attempt_id = attempt.id
        return attempt

    def complete_attempt(
        self,
        attempt_id: int,
        status: AttemptStatus,
        result: str = "",
        failure_reason: Optional[str] = None,
        observations: Optional[List[str]] = None,
    ) -> Attempt:
        """Mark an attempt as completed (succeeded or failed)."""
        attempt = self._attempts[attempt_id]
        attempt.status = status
        attempt.result = result
        attempt.failure_reason = failure_reason
        if observations:
            attempt.observations.extend(observations)
        if self._current_attempt_id == attempt_id:
            self._current_attempt_id = None
        return attempt

    def approaches_tried(self) -> List[int]:
        """Return IDs of approaches that have at least one attempt."""
        return list({a.approach_id for a in self._attempts.values()})

    def approaches_succeeded(self) -> List[int]:
        """Return IDs of approaches with at least one SUCCEEDED attempt."""
        return list({
            a.approach_id for a in self._attempts.values()
            if a.status == AttemptStatus.SUCCEEDED
        })

    def approaches_failed(self) -> List[int]:
        """Return IDs of approaches where ALL attempts FAILED."""
        tried = self.approaches_tried()
        succeeded = self.approaches_succeeded()
        return [aid for aid in tried if aid not in succeeded]

    def untried_approaches(self) -> List[Approach]:
        """Return approaches that have not been tried yet."""
        tried_ids = set(self.approaches_tried())
        return [
            a for a in self._approaches.values()
            if a.id not in tried_ids
        ]

    def current_attempt(self) -> Optional[Attempt]:
        """Return the in-progress attempt, if any."""
        if self._current_attempt_id is None:
            return None
        return self._attempts.get(self._current_attempt_id)

    def all_attempts(self) -> List[Attempt]:
        """Return all attempts."""
        return list(self._attempts.values())

    def summary(self) -> str:
        """Return a human-readable summary of the history."""
        return (
            f"Approaches: {len(self._approaches)} total, "
            f"{len(self.approaches_tried())} tried, "
            f"{len(self.approaches_succeeded())} succeeded, "
            f"{len(self.approaches_failed())} failed. "
            f"Attempts: {len(self._attempts)} total."
        )


def main() -> int:
    """CLI demo: exercise Approach, Attempt, and AttemptHistory."""
    print("=== MYTHRON Approach/Attempt demo ===")
    h = AttemptHistory()
    a1 = h.add_approach(Approach(name="http_port_scan", description="HTTP port scan", relevance=0.9, authorization=AuthorizationStatus.AUTHORIZED, scope=ScopeStatus.IN_SCOPE, expected_value=0.8))
    a2 = h.add_approach(Approach(name="dns_lookup", description="DNS recon", relevance=0.7, authorization=AuthorizationStatus.AUTHORIZED, scope=ScopeStatus.IN_SCOPE, expected_value=0.5))
    a3 = h.add_approach(Approach(name="ssh_brute", description="SSH brute (unauth)", relevance=0.4, authorization=AuthorizationStatus.UNAUTHORIZED, scope=ScopeStatus.OUT_OF_SCOPE, expected_value=0.1))
    print("\nApproaches:")
    for a in h.all_approaches():
        print(f"  [{a.id}] {a.name} priority={a.priority():.2f}")
    att1 = h.start_attempt(a1.id)
    h.complete_attempt(att1.id, AttemptStatus.FAILED, result="No HTTP ports (mock)", failure_reason="Target silent on HTTP", observations=["80 closed", "443 closed"])
    print(f"Attempt 1: {h.all_attempts()[-1].status.value} - {h.all_attempts()[-1].failure_reason}")
    att2 = h.start_attempt(a2.id)
    h.complete_attempt(att2.id, AttemptStatus.SUCCEEDED, result="Found DNS (mock)", observations=["A record", "MX record"])
    print(f"Attempt 2: {h.all_attempts()[-1].status.value}")
    print(f"\n{h.summary()}")
    print(f"Untried: {[a.name for a in h.untried_approaches()]}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
