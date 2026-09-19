from mythron.findings import Finding, FindingStore, Severity
from mythron.reporting import ReportGenerator


def test_generate_report_from_findings():
    store = FindingStore()
    store.add(
        Finding(
            title="Missing CSP",
            description="CSP header was not observed.",
            target="http://127.0.0.1:3000",
            severity=Severity.LOW,
            confidence=0.9,
            evidence=["CSP header missing"],
        )
    )

    report = ReportGenerator().generate(store)

    assert report.total_findings == 1
    assert report.findings[0].title == "Missing CSP"
    assert report.findings[0].severity == "LOW"
    assert report.findings[0].confidence == 0.9
    assert report.findings[0].verified is False
    assert report.findings[0].evidence == ["CSP header missing"]


def test_report_ignores_empty_evidence():
    store = FindingStore()
    store.add(
        Finding(
            title="Test Finding",
            description="Test description",
            target="http://127.0.0.1:3000",
            evidence=["Valid evidence", "   ", ""],
        )
    )

    report = ReportGenerator().generate(store)

    assert report.findings[0].evidence == ["Valid evidence"]


def test_report_summary_counts_severity():
    store = FindingStore()
    store.add(
        Finding(
            title="Low Finding",
            description="Low severity",
            target="http://127.0.0.1:3000",
            severity=Severity.LOW,
        )
    )
    store.add(
        Finding(
            title="Medium Finding",
            description="Medium severity",
            target="http://127.0.0.1:3000",
            severity=Severity.MEDIUM,
        )
    )

    report = ReportGenerator().generate(store)

    assert report.summary() == {
        "total": 2,
        "LOW": 1,
        "MEDIUM": 1,
    }
