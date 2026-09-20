"""MYTHRON — Controlled validation executor.

Performs narrowly scoped, non-destructive validation of approved findings.
This executor does not generate or execute arbitrary security payloads.
"""

from mythron.browser import BrowserAgent
from mythron.validation import (
    ValidationOutcome,
    ValidationRequest,
    ValidationResult,
)


class ValidationExecutor:
    """Execute explicitly approved, bounded validation plans."""

    SUPPORTED_CATEGORIES = {"http_response_header"}

    def __init__(self, browser: BrowserAgent | None = None) -> None:
        self._browser = browser or BrowserAgent(headless=True)

    def execute(self, request: ValidationRequest) -> ValidationResult:
        """Run a supported validation only after explicit approval."""

        if not request.approved:
            raise PermissionError(
                "Validation requires explicit approval before execution."
            )

        if request.status.value != "IN_PROGRESS":
            raise ValueError(
                "Validation request must be started before execution."
            )

        finding = request.finding

        if request.category not in self.SUPPORTED_CATEGORIES:
            return ValidationResult(
                outcome=ValidationOutcome.FAILED,
                summary="Unsupported validation category.",
                evidence=[
                    f"Validation category is not supported: {request.category}"
                ],
            )

        started_here = False

        try:
            if not self._browser.is_started:
                self._browser.start()
                started_here = True

            observation = self._browser.inspect(finding.target)
            has_csp = observation.has_header("content-security-policy")

            if has_csp:
                return ValidationResult(
                    outcome=ValidationOutcome.NOT_CONFIRMED,
                    summary=(
                        "Content-Security-Policy was observed during "
                        "controlled validation."
                    ),
                    evidence=[
                        "Validation response contained "
                        "Content-Security-Policy."
                    ],
                )

            return ValidationResult(
                outcome=ValidationOutcome.CONFIRMED,
                summary=(
                    "Controlled validation confirmed that the observed "
                    "response does not contain Content-Security-Policy."
                ),
                evidence=[
                    "Validation response did not contain "
                    "Content-Security-Policy.",
                    f"Validated URL: {observation.url}",
                    f"Response title: {observation.title}",
                ],
            )

        except Exception as exc:
            return ValidationResult(
                outcome=ValidationOutcome.FAILED,
                summary="Controlled validation failed.",
                evidence=[str(exc)],
            )

        finally:
            if started_here:
                self._browser.stop()
