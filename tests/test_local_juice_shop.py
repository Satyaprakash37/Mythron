from mythron.approaches import Approach, AuthorizationStatus, ScopeStatus
from mythron.assessment import Assessment, AssessmentScope
from mythron.assessment_engine import AssessmentEngine
from mythron.browser_executor import BrowserApproachExecutor
from mythron.capabilities import Capability, CapabilityRegistry


def test_local_juice_shop_passive_browser_assessment():
    target = "http://127.0.0.1:3000"

    assessment = Assessment(
        name="Local Juice Shop Assessment",
        scope=AssessmentScope(
            target=target,
            authorized=True,
            allowed_capabilities=["browser"],
        ),
    )

    registry = CapabilityRegistry()
    registry.register(
        Capability(
            name="browser",
            description="Controlled passive browser inspection",
            category="assessment",
            enabled=True,
        )
    )

    engine = AssessmentEngine(
        assessment=assessment,
        capabilities=registry,
        executors={"browser": BrowserApproachExecutor()},
    )

    assessment.start()

    approach = Approach(
        name="browser_inspect",
        description=target,
        relevance=1.0,
        authorization=AuthorizationStatus.AUTHORIZED,
        scope=ScopeStatus.IN_SCOPE,
        expected_value=1.0,
    )

    execution = engine.execute(
        capability_name="browser",
        approach=approach,
    )

    assert execution.allowed is True
    assert execution.result is not None
    assert execution.result.status.value == "SUCCEEDED"
    assert execution.result.data is not None
    assert assessment.findings_count >= 1
