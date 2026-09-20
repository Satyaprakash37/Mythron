from mythron.assessment import Assessment, AssessmentScope
from mythron.assessment_engine import AssessmentEngine
from mythron.capabilities import Capability, CapabilityRegistry
from mythron.executors import ExecutionResult
from mythron.approaches import AttemptStatus
from mythron.controller import AssessmentController


class FakeExecutor:
    name = "browser"

    def can_execute(self, approach):
        return approach.name == "browser_inspect"

    def execute(self, approach):
        return ExecutionResult(
            status=AttemptStatus.SUCCEEDED,
            result="controlled browser inspection",
            observations=["local target observed"],
        )


def make_controller():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
        allowed_capabilities=["browser"],
    )

    assessment = Assessment(
        name="Local Juice Shop Assessment",
        scope=scope,
    )

    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="browser",
            description="Controlled browser inspection",
            category="assessment",
            enabled=True,
        )
    )

    engine = AssessmentEngine(
        assessment=assessment,
        capabilities=registry,
        executors={"browser": FakeExecutor()},
    )

    return assessment, AssessmentController(engine)


def test_controller_starts_authorized_assessment():
    assessment, controller = make_controller()

    controller.start()

    assert assessment.status.value == "ACTIVE"


def test_controller_reports_target():
    _, controller = make_controller()

    assert controller.target == "http://127.0.0.1:3000"


def test_controller_executes_through_assessment_engine():
    _, controller = make_controller()

    controller.start()

    result = controller.execute(
        capability_name="browser",
        approach_name="browser_inspect",
        target="http://127.0.0.1:3000",
    )

    assert result.allowed is True
    assert result.result is not None
    assert result.result.status == AttemptStatus.SUCCEEDED


def test_controller_rejects_target_mismatch():
    _, controller = make_controller()

    controller.start()

    result = controller.execute(
        capability_name="browser",
        approach_name="browser_inspect",
        target="http://127.0.0.1:4000",
    )

    assert result.allowed is False
    assert "target does not match" in result.reason
