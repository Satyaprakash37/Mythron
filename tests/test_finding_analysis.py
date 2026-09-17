from mythron.findings import Finding, Severity
from mythron.finding_analysis import FindingAnalyzer


def test_high_confidence_finding_is_actionable():
    finding = Finding(
        title="Missing CSP",
        description="CSP header was not observed.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
        evidence=["CSP header missing"],
    )

    analysis = FindingAnalyzer().analyze(finding)

    assert analysis.is_actionable() is True
    assert analysis.validation_needed is True


def test_low_confidence_finding_is_not_actionable():
    finding = Finding(
        title="Possible Issue",
        description="Potential issue.",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.5,
        evidence=["Weak observation"],
    )

    analysis = FindingAnalyzer().analyze(finding)

    assert analysis.is_actionable() is False
    assert analysis.validation_needed is True


def test_finding_without_evidence_is_not_actionable():
    finding = Finding(
        title="Unknown Issue",
        description="Needs more evidence.",
        target="http://127.0.0.1:3000",
        severity=Severity.INFO,
        confidence=0.9,
    )

    analysis = FindingAnalyzer().analyze(finding)

    assert analysis.is_actionable() is False
    assert analysis.validation_needed is True


def test_verified_finding_does_not_need_validation():
    finding = Finding(
        title="Verified Finding",
        description="Already validated.",
        target="http://127.0.0.1:3000",
        severity=Severity.MEDIUM,
        confidence=0.9,
        evidence=["Controlled evidence"],
        verified=True,
    )

    analysis = FindingAnalyzer().analyze(finding)

    assert analysis.validation_needed is False
