import pytest

from mythron.assessment import (
    Assessment,
    AssessmentScope,
    AssessmentStatus,
)


def test_authorized_assessment_can_start():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
        allowed_capabilities=["browser_inspect"],
    )

    assessment = Assessment(
        name="Juice Shop Local Assessment",
        scope=scope,
    )

    assessment.start()

    assert assessment.status == AssessmentStatus.ACTIVE
    assert assessment.can_use_capability("browser_inspect")


def test_unauthorized_assessment_cannot_start():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=False,
        allowed_capabilities=["browser_inspect"],
    )

    assessment = Assessment(
        name="Unauthorized Assessment",
        scope=scope,
    )

    with pytest.raises(PermissionError):
        assessment.start()

    assert assessment.status == AssessmentStatus.CREATED


def test_unlisted_capability_is_rejected():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
        allowed_capabilities=["browser_inspect"],
    )

    assessment = Assessment(
        name="Scoped Assessment",
        scope=scope,
    )

    assessment.start()

    assert assessment.can_use_capability("browser_inspect")
    assert not assessment.can_use_capability("unknown_capability")


def test_lifecycle_stop_blocks_capabilities():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
        allowed_capabilities=["browser_inspect"],
    )

    assessment = Assessment(
        name="Lifecycle Assessment",
        scope=scope,
    )

    assessment.start()
    assessment.stop()

    assert assessment.status == AssessmentStatus.STOPPED
    assert not assessment.can_use_capability("browser_inspect")


def test_scope_allows_exact_target():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
    )

    assert scope.allows_target("http://127.0.0.1:3000")


def test_scope_rejects_different_target():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=True,
    )

    assert not scope.allows_target("http://127.0.0.1:4000")


def test_unauthorized_scope_rejects_target():
    scope = AssessmentScope(
        target="http://127.0.0.1:3000",
        authorized=False,
    )

    assert not scope.allows_target("http://127.0.0.1:3000")
