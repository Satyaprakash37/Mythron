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
from mythron.findings import Finding, FindingStore
from mythron.browser import BrowserObservation
from mythron.discovery import DiscoveryEngine
from mythron.security_signals import SecuritySignalDetector
from mythron.finding_analysis import FindingAnalysis, FindingAnalyzer
from mythron.validation import (
    ValidationOutcome,
    ValidationRequest,
    ValidationResult,
)
from mythron.validation_executor import ValidationExecutor
from mythron.evidence import EvidenceCollector
from mythron.reporting import AssessmentReport, ReportGenerator


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
        discovery: DiscoveryEngine | None = None,
        security_signal_detector: SecuritySignalDetector | None = None,
        finding_analyzer: FindingAnalyzer | None = None,
        validation_executor: ValidationExecutor | None = None,
    ) -> None:
        self._assessment = assessment
        self._capabilities = capabilities
        self._executors = executors
        self._discovery = discovery or DiscoveryEngine()
        self._security_signal_detector = (
            security_signal_detector or SecuritySignalDetector()
        )
        self._security_signal_findings = FindingStore()
        self._finding_analyzer = finding_analyzer or FindingAnalyzer()
        self._validation_executor = validation_executor or ValidationExecutor()
        self._evidence_collector = EvidenceCollector()
        self._report_generator = ReportGenerator(self._evidence_collector)

    def record_discovery(self, observation: BrowserObservation) -> Finding:
        """Record a controlled browser observation as discovery inventory."""
        if not self._assessment.scope.authorized:
            raise PermissionError("Discovery requires an authorized assessment.")

        if not self._assessment.scope.allows_target(observation.url):
            raise PermissionError(
                "Discovery target does not match the authorized assessment target."
            )

        result = self._discovery.record(observation)

        before_count = len(self._discovery.findings().all())
        finding = self._discovery.store_inventory_finding(result)
        after_count = len(self._discovery.findings().all())

        if after_count > before_count:
            self._assessment.findings_count += 1

        return finding

    def analyze_security_signals(
        self,
        observation: BrowserObservation,
    ) -> list[Finding]:
        """Analyze an authorized observation for passive security signals."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Security signal analysis requires an authorized assessment."
            )

        if not self._assessment.scope.allows_target(observation.url):
            raise PermissionError(
                "Security signal target does not match the authorized assessment target."
            )

        findings = self._security_signal_detector.analyze(observation)

        new_findings = 0
        for finding in findings:
            before_count = len(self._security_signal_findings.all())
            stored = self._security_signal_findings.add(finding)
            after_count = len(self._security_signal_findings.all())

            if after_count > before_count:
                new_findings += 1

        self._assessment.findings_count += new_findings
        return findings

    def analyze_finding(self, finding: Finding) -> FindingAnalysis:
        """Analyze a finding using the configured finding analyzer."""
        return self._finding_analyzer.analyze(finding)

    def collect_evidence(self, finding: Finding) -> list[str]:
        """Collect existing evidence from a finding without modifying it."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Evidence collection requires an authorized assessment."
            )

        if not self._assessment.scope.allows_target(finding.target):
            raise PermissionError(
                "Evidence target does not match the authorized assessment target."
            )

        return self._evidence_collector.collect(finding)

    def request_validation(self, finding: Finding) -> ValidationRequest:
        """Create a controlled validation request for a finding."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Validation requires an authorized assessment."
            )

        if not self._assessment.scope.allows_target(finding.target):
            raise PermissionError(
                "Validation target does not match the authorized assessment target."
            )

        return ValidationRequest(finding=finding)

    def start_validation(
        self,
        request: ValidationRequest,
    ) -> ValidationRequest:
        """Start a validation request after its approval checks."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Validation requires an authorized assessment."
            )

        if not self._assessment.scope.allows_target(request.finding.target):
            raise PermissionError(
                "Validation target does not match the authorized assessment target."
            )

        request.start()
        return request

    def execute_validation(
        self,
        request: ValidationRequest,
    ) -> ValidationResult:
        """Execute an approved validation and record its result."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Validation requires an authorized assessment."
            )

        if not self._assessment.scope.allows_target(request.finding.target):
            raise PermissionError(
                "Validation target does not match the authorized assessment target."
            )

        result = self._validation_executor.execute(request)

        for evidence in result.evidence:
            request.finding.add_evidence(evidence)

        if result.outcome in {
            ValidationOutcome.CONFIRMED,
            ValidationOutcome.NOT_CONFIRMED,
        }:
            request.complete()

        return result

    def complete_validation(
        self,
        request: ValidationRequest,
    ) -> ValidationRequest:
        """Complete an active validation request."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Validation requires an authorized assessment."
            )

        if not self._assessment.scope.allows_target(request.finding.target):
            raise PermissionError(
                "Validation target does not match the authorized assessment target."
            )

        request.complete()
        return request

    def generate_report(self) -> AssessmentReport:
        """Generate a report from the assessment's collected findings."""
        if not self._assessment.scope.authorized:
            raise PermissionError(
                "Report generation requires an authorized assessment."
            )

        combined_store = FindingStore()

        for finding in self._discovery.findings().all():
            combined_store.add(finding)

        for finding in self._security_signal_findings.all():
            combined_store.add(finding)

        return self._report_generator.generate(combined_store)

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

        if not self._assessment.scope.allows_target(approach.description):
            return AssessmentExecution(
                allowed=False,
                reason="Approach target does not match the authorized assessment target.",
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

        # Automatically process structured browser observations.
        # This is passive analysis only; no exploitation is performed.
        if isinstance(result.data, BrowserObservation):
            self.record_discovery(result.data)
            self.analyze_security_signals(result.data)

        return AssessmentExecution(
            allowed=True,
            result=result,
        )
