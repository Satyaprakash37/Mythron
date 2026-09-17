from mythron.browser import BrowserObservation
from mythron.security_signals import SecuritySignalDetector
from mythron.findings import Severity


def test_detector_reports_missing_content_security_policy():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="",
        headers={
            "x-content-type-options": "nosniff",
            "x-frame-options": "SAMEORIGIN",
        },
    )

    detector = SecuritySignalDetector()
    findings = detector.analyze(observation)

    csp_findings = [
        finding
        for finding in findings
        if finding.title == "Missing Content-Security-Policy Header"
    ]

    assert len(csp_findings) == 1
    assert csp_findings[0].severity == Severity.LOW
    assert csp_findings[0].confidence == 1.0
    assert any("content-security-policy" in item.lower()
               for item in csp_findings[0].evidence)


def test_detector_does_not_report_csp_when_present():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="",
        headers={
            "content-security-policy": "default-src 'self'",
        },
    )

    detector = SecuritySignalDetector()
    findings = detector.analyze(observation)

    assert not any(
        finding.title == "Missing Content-Security-Policy Header"
        for finding in findings
    )


def test_detector_reports_missing_hsts_on_https():
    observation = BrowserObservation(
        url="https://example.com/",
        title="Example",
        text="",
        headers={
            "content-type": "text/html",
        },
    )

    detector = SecuritySignalDetector()
    findings = detector.analyze(observation)

    hsts_findings = [
        finding
        for finding in findings
        if finding.title == "Missing Strict-Transport-Security Header"
    ]

    assert len(hsts_findings) == 1
    assert hsts_findings[0].severity == Severity.LOW
    assert hsts_findings[0].confidence == 1.0


def test_detector_does_not_report_hsts_missing_on_http():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="",
        headers={},
    )

    detector = SecuritySignalDetector()
    findings = detector.analyze(observation)

    assert not any(
        finding.title == "Missing Strict-Transport-Security Header"
        for finding in findings
    )


def test_detector_does_not_report_hsts_when_present():
    observation = BrowserObservation(
        url="https://example.com/",
        title="Example",
        text="",
        headers={
            "strict-transport-security": "max-age=31536000",
        },
    )

    detector = SecuritySignalDetector()
    findings = detector.analyze(observation)

    assert not any(
        finding.title == "Missing Strict-Transport-Security Header"
        for finding in findings
    )
