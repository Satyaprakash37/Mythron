import pytest

from mythron.findings import Finding, Severity
from mythron.validation import (
    ValidationRequest,
    ValidationStatus,
)


def make_finding():
    return Finding(
        title="Test Finding",
        description="Controlled validation test",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["Observed evidence"],
    )


def test_validation_request_starts_pending():
    request = ValidationRequest(finding=make_finding())

    assert request.status == ValidationStatus.PENDING
    assert request.approved is False


def test_validation_request_requires_explicit_approval():
    request = ValidationRequest(finding=make_finding())

    with pytest.raises(PermissionError):
        request.start()

    assert request.status == ValidationStatus.PENDING


def test_validation_request_can_be_approved_and_started():
    request = ValidationRequest(finding=make_finding())

    request.approve()
    request.start()

    assert request.approved is True
    assert request.status == ValidationStatus.IN_PROGRESS


def test_validation_request_can_be_rejected():
    request = ValidationRequest(finding=make_finding())

    request.reject()

    assert request.approved is False
    assert request.status == ValidationStatus.REJECTED


def test_validation_request_can_complete():
    request = ValidationRequest(finding=make_finding())

    request.approve()
    request.start()
    request.complete()

    assert request.status == ValidationStatus.COMPLETED


def test_validation_request_cannot_complete_without_start():
    request = ValidationRequest(finding=make_finding())

    request.approve()

    with pytest.raises(ValueError):
        request.complete()


def test_approval_marks_finding_for_validation():
    finding = make_finding()
    request = ValidationRequest(finding=finding)

    request.approve()

    assert finding.validation_requested is True


def test_completed_validation_verifies_finding():
    finding = make_finding()
    request = ValidationRequest(finding=finding)

    request.approve()
    request.start()
    request.complete()

    assert finding.verified is True
