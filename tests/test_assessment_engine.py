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
