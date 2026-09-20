from mythron.browser import BrowserObservation
from mythron.findings import Finding, Severity
from mythron.validation import (
    ValidationOutcome,
    ValidationRequest,
)
from mythron.validation_executor import ValidationExecutor


class FakeBrowser:
    """Small browser double for deterministic validation tests."""

    def __init__(self, observation):
        self.observation = observation
        self.started = False
        self.stopped = False

    @property
    def is_started(self):
        return self.started

    def start(self):
        self.started = True

    def stop(self):
        self.stopped = True
        self.started = False

    def inspect(self, url):
        return self.observation


def make_finding():
    return Finding(
        title="Missing Content-Security-Policy Header",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=1.0,
        evidence=["CSP header missing"],
    )


def make_request():
    request = ValidationRequest(finding=make_finding())
    request.approve()
    request.start()
    return request


def make_observation(headers=None):
    return BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="OWASP Juice Shop",
        text="Juice Shop",
        headers=headers or {},
    )


def test_validation_executor_confirms_missing_csp():
    browser = FakeBrowser(make_observation())
    executor = ValidationExecutor(browser=browser)

    result = executor.execute(make_request())

    assert result.outcome == ValidationOutcome.CONFIRMED
    assert "does not contain" in result.summary
    assert result.evidence
    assert browser.stopped is True


def test_validation_executor_does_not_confirm_when_csp_exists():
    browser = FakeBrowser(
        make_observation(
            headers={"content-security-policy": "default-src 'self'"}
        )
    )
    executor = ValidationExecutor(browser=browser)

    result = executor.execute(make_request())

    assert result.outcome == ValidationOutcome.NOT_CONFIRMED
    assert "was observed" in result.summary


def test_validation_executor_requires_started_request():
    finding = make_finding()
    request = ValidationRequest(finding=finding)
    request.approve()

    executor = ValidationExecutor(
        browser=FakeBrowser(make_observation())
    )

    try:
        executor.execute(request)
    except ValueError as exc:
        assert "started" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_validation_executor_rejects_unsupported_finding():
    finding = Finding(
        title="Different Finding",
        description="Unsupported validation",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=1.0,
        evidence=["Evidence"],
    )

    request = ValidationRequest(finding=finding)
    request.approve()
    request.start()

    executor = ValidationExecutor(
        browser=FakeBrowser(make_observation())
    )

    result = executor.execute(request)

    assert result.outcome == ValidationOutcome.FAILED
    assert "Unsupported" in result.summary
