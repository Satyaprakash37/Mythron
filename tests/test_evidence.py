from mythron.evidence import EvidenceCollector
from mythron.findings import Finding, Severity


def test_collect_finding_evidence():
    finding = Finding(
        title="Missing CSP",
        description="CSP header is missing.",
        target="http://127.0.0.1:3000",
        severity=Severity.MEDIUM,
        evidence=["CSP header missing"],
    )

    collector = EvidenceCollector()
    evidence = collector.collect(finding)

    assert evidence == [
        "CSP header missing",
    ]


def test_collect_ignores_empty_evidence():
    finding = Finding(
        title="Test",
        description="Test finding",
        target="http://127.0.0.1:3000",
        evidence=["Valid evidence", "   ", ""],
    )

    collector = EvidenceCollector()
    evidence = collector.collect(finding)

    assert evidence == ["Valid evidence"]


def test_collect_does_not_modify_finding():
    finding = Finding(
        title="Test",
        description="Test finding",
        target="http://127.0.0.1:3000",
        evidence=["Observed evidence"],
    )

    collector = EvidenceCollector()
    collector.collect(finding)

    assert finding.evidence == ["Observed evidence"]
