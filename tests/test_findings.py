from mythron.findings import Finding, FindingStore, Severity


def test_finding_defaults():
    finding = Finding(
        title="Test Finding",
        description="Example security finding",
        target="http://127.0.0.1:3000",
    )

    assert finding.severity == Severity.INFO
    assert finding.confidence == 0.0
    assert finding.verified is False
    assert finding.validation_requested is False
    assert finding.evidence == []


def test_finding_evidence():
    finding = Finding(
        title="Test Finding",
        description="Example",
        target="http://127.0.0.1:3000",
    )

    finding.add_evidence("Observed suspicious behavior")
    finding.add_evidence("Second observation")
    finding.add_evidence("   ")

    assert finding.evidence == [
        "Observed suspicious behavior",
        "Second observation",
    ]


def test_confidence_threshold():
    finding = Finding(
        title="High Confidence Finding",
        description="Example",
        target="http://127.0.0.1:3000",
        severity=Severity.HIGH,
        confidence=0.9,
    )

    assert finding.is_high_confidence()


def test_validation_and_verification():
    finding = Finding(
        title="Potential Finding",
        description="Requires controlled validation",
        target="http://127.0.0.1:3000",
        severity=Severity.MEDIUM,
        confidence=0.85,
    )

    finding.request_validation()

    assert finding.validation_requested is True
    assert finding.verified is False

    finding.mark_verified()

    assert finding.verified is True

def test_finding_store_tracks_findings():
    from mythron.findings import FindingStore

    store = FindingStore()

    first = Finding(
        title="Exposed Login Endpoint",
        description="A login endpoint was observed during authorized discovery.",
        target="http://127.0.0.1:3000/login",
        severity=Severity.INFO,
        confidence=0.9,
    )

    second = Finding(
        title="Observed Search Endpoint",
        description="A search endpoint was observed.",
        target="http://127.0.0.1:3000/search",
        severity=Severity.INFO,
        confidence=0.7,
    )

    store.add(first)
    store.add(second)

    assert len(store.all()) == 2
    assert store.all()[0] is first
    assert store.all()[1] is second


def test_finding_store_summary():
    from mythron.findings import FindingStore

    store = FindingStore()

    store.add(
        Finding(
            title="High Finding",
            description="Example",
            target="http://127.0.0.1:3000",
            severity=Severity.HIGH,
            confidence=0.9,
        )
    )

    store.add(
        Finding(
            title="Low Finding",
            description="Example",
            target="http://127.0.0.1:3000",
            severity=Severity.LOW,
            confidence=0.6,
        )
    )

    summary = store.summary()

    assert summary["total"] == 2
    assert summary["HIGH"] == 1
    assert summary["LOW"] == 1


def test_finding_store_deduplicates_same_finding():
    store = FindingStore()

    finding = Finding(
        title="Test Finding",
        description="Same issue",
        target="http://127.0.0.1:3000",
        severity=Severity.LOW,
        confidence=0.9,
    )

    store.add(finding)
    store.add(finding)

    assert len(store.all()) == 1
