import pytest
from mythron.approaches import (
    Approach,
    AuthorizationStatus,
    ScopeStatus,
)
from mythron.assessment import Assessment, AssessmentScope
from mythron.assessment_engine import AssessmentEngine
from mythron.capabilities import Capability, CapabilityRegistry
from mythron.executors import ExecutionResult
from mythron.approaches import AttemptStatus


class FakeExecutor:
    name = "browser"

    def can_execute(self, approach):
        return approach.name == "browser_inspect"

    def execute(self, approach):
        return ExecutionResult(
            status=AttemptStatus.SUCCEEDED,
            result="fake execution succeeded",
            observations=["test observation"],
        )


def make_engine():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
        allowed_capabilities=["browser"],
    )

    assessment = Assessment(
        name="Local Juice Shop Assessment",
        scope=scope,
    )
    assessment.start()

    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="browser",
            description="Controlled browser inspection",
            category="assessment",
            requires_authorization=True,
            enabled=True,
        )
    )

    return assessment, AssessmentEngine(
        assessment=assessment,
        capabilities=registry,
        executors={"browser": FakeExecutor()},
    )


def make_approach():
    return Approach(
        name="browser_inspect",
        description="http://127.0.0.1:3000",
        relevance=1.0,
        authorization=AuthorizationStatus.AUTHORIZED,
        scope=ScopeStatus.IN_SCOPE,
        expected_value=1.0,
    )


def test_authorized_in_scope_execution():
    _, engine = make_engine()

    execution = engine.execute("browser", make_approach())

    assert execution.allowed is True
    assert execution.result is not None
    assert execution.result.status == AttemptStatus.SUCCEEDED


def test_unauthorized_assessment_is_blocked():
    assessment, engine = make_engine()
    assessment.scope.authorized = False

    execution = engine.execute("browser", make_approach())

    assert execution.allowed is False
    assert "not authorized" in execution.reason


def test_out_of_scope_approach_is_blocked():
    _, engine = make_engine()

    approach = make_approach()
    approach.scope = ScopeStatus.OUT_OF_SCOPE

    execution = engine.execute("browser", approach)

    assert execution.allowed is False
    assert "authorized and in scope" in execution.reason


def test_unallowed_capability_is_blocked():
    _, engine = make_engine()

    execution = engine.execute("unknown_capability", make_approach())

    assert execution.allowed is False
    assert "not allowed" in execution.reason


def test_disabled_capability_is_blocked():
    assessment, engine = make_engine()

    # Rebuild registry with disabled capability.
    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="browser",
            description="Controlled browser inspection",
            category="assessment",
            enabled=False,
        )
    )

    disabled_engine = AssessmentEngine(
        assessment=assessment,
        capabilities=registry,
        executors={"browser": FakeExecutor()},
    )

    execution = disabled_engine.execute("browser", make_approach())

    assert execution.allowed is False
    assert "disabled" in execution.reason


def test_different_target_is_blocked():
    _, engine = make_engine()

    approach = make_approach()
    approach.description = "http://127.0.0.1:4000"

    execution = engine.execute("browser", approach)

    assert execution.allowed is False
    assert "target does not match" in execution.reason

def test_assessment_engine_can_store_discovery_inventory():
    from mythron.browser import BrowserObservation
    from mythron.discovery import DiscoveryEngine

    assessment, base_engine = make_engine()
    discovery = DiscoveryEngine()

    assessment_engine = AssessmentEngine(
        assessment=assessment,
        capabilities=base_engine._capabilities,
        executors=base_engine._executors,
        discovery=discovery,
    )

    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="Authorized local application",
        links=["http://127.0.0.1:3000/login"],
        forms=[],
    )

    finding = assessment_engine.record_discovery(observation)

    assert finding.target == observation.url
    assert finding.title == "Discovered Web Application Surface"
    assert len(discovery.findings().all()) == 1
    assert assessment.findings_count == 1

    assessment_engine.record_discovery(observation)

    assert len(discovery.findings().all()) == 1
    assert assessment.findings_count == 1


def test_assessment_engine_can_analyze_security_signals():
    from mythron.browser import BrowserObservation
    from mythron.discovery import DiscoveryEngine
    from mythron.security_signals import SecuritySignalDetector

    assessment, base_engine = make_engine()

    assessment_engine = AssessmentEngine(
        assessment=assessment,
        capabilities=base_engine._capabilities,
        executors=base_engine._executors,
        discovery=DiscoveryEngine(),
        security_signal_detector=SecuritySignalDetector(),
    )

    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="Authorized local application",
        headers={
            "x-content-type-options": "nosniff",
            "x-frame-options": "SAMEORIGIN",
        },
    )

    findings = assessment_engine.analyze_security_signals(observation)

    assert len(findings) == 1
    assert findings[0].title == "Missing Content-Security-Policy Header"
    assert findings[0].target == observation.url
    assert assessment.findings_count == 1


def test_assessment_engine_can_analyze_finding():
    from mythron.findings import Finding, Severity

    _, engine = make_engine()

    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["CSP header missing"],
    )

    analysis = engine.analyze_finding(finding)

    assert analysis.finding is finding
    assert analysis.validation_needed is True
    assert analysis.is_actionable() is True


def test_assessment_engine_can_create_validation_request():
    from mythron.findings import Finding, Severity

    _, engine = make_engine()

    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["CSP header missing"],
    )

    request = engine.request_validation(finding)

    assert request.finding is finding
    assert request.status.value == "PENDING"
    assert request.approved is False


def test_assessment_engine_can_start_approved_validation():
    from mythron.findings import Finding, Severity

    _, engine = make_engine()

    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["CSP header missing"],
    )

    request = engine.request_validation(finding)
    request.approve()

    started = engine.start_validation(request)

    assert started.status.value == "IN_PROGRESS"


def test_assessment_engine_can_complete_validation():
    from mythron.findings import Finding, Severity

    _, engine = make_engine()

    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["CSP header missing"],
    )

    request = engine.request_validation(finding)
    request.approve()
    engine.start_validation(request)

    completed = engine.complete_validation(request)

    assert completed.status.value == "COMPLETED"
    assert finding.verified is True


def test_assessment_engine_can_collect_finding_evidence():
    from mythron.findings import Finding, Severity

    _, engine = make_engine()

    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        evidence=["CSP header missing", "   ", ""],
    )

    evidence = engine.collect_evidence(finding)

    assert evidence == ["CSP header missing"]


def test_assessment_engine_can_generate_report_from_security_findings():
    from mythron.findings import Finding, Severity

    _, engine = make_engine()

    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["CSP header missing"],
    )

    engine._security_signal_findings.add(finding)

    report = engine.generate_report()

    assert report.total_findings == 1
    assert report.findings[0].title == "Missing CSP"
    assert report.findings[0].severity == "LOW"
    assert report.findings[0].evidence == ["CSP header missing"]


def test_assessment_engine_report_requires_authorized_assessment():
    from mythron.findings import Finding, Severity

    assessment, engine = make_engine()
    assessment.scope.authorized = False

    finding = Finding(
        title="Test Finding",
        description="Test",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
    )

    engine._security_signal_findings.add(finding)

    with pytest.raises(PermissionError):
        engine.generate_report()


def test_complete_local_assessment_flow():
    from mythron.browser import BrowserObservation
    from mythron.discovery import DiscoveryEngine
    from mythron.security_signals import SecuritySignalDetector

    assessment, base_engine = make_engine()

    engine = AssessmentEngine(
        assessment=assessment,
        capabilities=base_engine._capabilities,
        executors=base_engine._executors,
        discovery=DiscoveryEngine(),
        security_signal_detector=SecuritySignalDetector(),
    )

    # 1. Observe the authorized local target.
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="Authorized local application",
        links=["http://127.0.0.1:3000/login"],
        forms=[],
        headers={
            "x-content-type-options": "nosniff",
            "x-frame-options": "SAMEORIGIN",
        },
    )

    # 2. Record discovery inventory.
    inventory_finding = engine.record_discovery(observation)

    assert inventory_finding.target == observation.url

    # 3. Analyze passive security signals.
    findings = engine.analyze_security_signals(observation)

    assert len(findings) == 1

    finding = findings[0]
    assert finding.title == "Missing Content-Security-Policy Header"

    # 4. Analyze the finding.
    analysis = engine.analyze_finding(finding)

    assert analysis.finding is finding
    assert analysis.is_actionable() is True

    # 5. Request validation.
    request = engine.request_validation(finding)

    assert request.approved is False
    assert request.status.value == "PENDING"

    # 6. Explicit human approval.
    request.approve()

    assert request.approved is True
    assert finding.validation_requested is True

    # 7. Start controlled validation.
    engine.start_validation(request)

    assert request.status.value == "IN_PROGRESS"

    # 8. Complete controlled validation.
    engine.complete_validation(request)

    assert request.status.value == "COMPLETED"
    assert finding.verified is True

    # 9. Collect existing evidence.
    evidence = engine.collect_evidence(finding)

    assert evidence == finding.evidence

    # 10. Generate final report.
    report = engine.generate_report()

    assert report.total_findings == 2
    assert any(
        item.title == finding.title
        and item.verified is True
        for item in report.findings
    )
