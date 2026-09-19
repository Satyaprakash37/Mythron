"""MYTHRON Phase 9 — Evaluation framework.

Provides small, deterministic evaluation models for controlled
assessment and agent behavior testing.
"""

from dataclasses import dataclass


@dataclass
class EvaluationCase:
    """Represent one controlled evaluation scenario."""

    name: str
    objective: str
    expected: str
    actual: str
    notes: str = ""

    @property
    def passed(self) -> bool:
        """Return True when the actual result matches the expected result."""
        return self.actual == self.expected


class EvaluationSuite:
    """Collect and summarize controlled evaluation cases."""

    def __init__(self) -> None:
        self._cases: list[EvaluationCase] = []

    def add(self, case: EvaluationCase) -> EvaluationCase:
        """Add an evaluation case and return it."""
        if any(existing.name == case.name for existing in self._cases):
            raise ValueError("Evaluation case name already exists.")

        self._cases.append(case)
        return case

    def all(self) -> list[EvaluationCase]:
        """Return all evaluation cases."""
        return list(self._cases)

    def run(self) -> EvaluationResult:
        """Run the evaluation suite and return its result."""
        return EvaluationResult.from_suite(self)


    @property
    def passed(self) -> bool:
        """Return True only when every case passes."""
        return all(case.passed for case in self._cases)

    def summary(self) -> dict[str, int]:
        """Return total, passed, and failed case counts."""
        passed = sum(1 for case in self._cases if case.passed)
        total = len(self._cases)

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        }


@dataclass
class EvaluationResult:
    """Store the result of one completed evaluation suite."""

    passed: bool
    summary: dict[str, int]
    failed_cases: list[str]
    case_statuses: dict[str, bool]

    @classmethod
    def from_suite(cls, suite: EvaluationSuite) -> "EvaluationResult":
        """Build an evaluation result from a completed suite."""
        return cls(
            passed=suite.passed,
            summary=suite.summary(),
            failed_cases=[
                case.name
                for case in suite.all()
                if not case.passed
            ],
            case_statuses={
                case.name: case.passed
                for case in suite.all()
            },
        )
