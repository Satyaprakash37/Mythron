from mythron.browser import BrowserObservation
from mythron.discovery import DiscoveryEngine


def test_discovery_engine_collects_browser_observation():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="OWASP Juice Shop",
        text="OWASP Juice Shop",
        links=[
            "http://127.0.0.1:3000/#/login",
            "http://127.0.0.1:3000/#/search",
        ],
        forms=[
            "POST http://127.0.0.1:3000/rest/user/login",
        ],
    )

    engine = DiscoveryEngine()
    result = engine.record(observation)

    assert result.target == "http://127.0.0.1:3000/"
    assert result.title == "OWASP Juice Shop"
    assert len(result.links) == 2
    assert len(result.forms) == 1


def test_discovery_engine_deduplicates_links():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Test",
        text="Test",
        links=[
            "http://127.0.0.1:3000/login",
            "http://127.0.0.1:3000/login",
        ],
    )

    engine = DiscoveryEngine()
    result = engine.record(observation)

    assert result.links == [
        "http://127.0.0.1:3000/login"
    ]

def test_discovery_engine_preserves_forms_and_text():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/login",
        title="Login",
        text="Username Password Login",
        links=[],
        forms=[
            "POST http://127.0.0.1:3000/rest/user/login",
            "POST http://127.0.0.1:3000/rest/user/login",
        ],
    )

    engine = DiscoveryEngine()
    result = engine.record(observation)

    assert result.text == "Username Password Login"
    assert result.forms == [
        "POST http://127.0.0.1:3000/rest/user/login"
    ]

def test_discovery_engine_tracks_multiple_observations():
    engine = DiscoveryEngine()

    first = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Home",
        text="Home page",
        links=["http://127.0.0.1:3000/login"],
    )

    second = BrowserObservation(
        url="http://127.0.0.1:3000/login",
        title="Login",
        text="Login page",
        links=[],
    )

    engine.record(first)
    engine.record(second)

    assert hasattr(engine, "results")
    assert len(engine.results()) == 2
    assert engine.results()[0].target == "http://127.0.0.1:3000/"
    assert engine.results()[1].target == "http://127.0.0.1:3000/login"

def test_discovery_engine_summarizes_inventory():
    engine = DiscoveryEngine()

    engine.record(
        BrowserObservation(
            url="http://127.0.0.1:3000/",
            title="Home",
            text="Home",
            links=[
                "http://127.0.0.1:3000/login",
                "http://127.0.0.1:3000/search",
            ],
            forms=[
                "POST http://127.0.0.1:3000/rest/user/login",
            ],
        )
    )

    engine.record(
        BrowserObservation(
            url="http://127.0.0.1:3000/login",
            title="Login",
            text="Login",
        )
    )

    summary = engine.summary()

    assert summary["pages"] == 2
    assert summary["unique_links"] == 2
    assert summary["unique_forms"] == 1

def test_discovery_can_create_inventory_findings():
    from mythron.findings import Finding, FindingStore, Severity

    engine = DiscoveryEngine()
    store = FindingStore()

    observation = BrowserObservation(
        url="http://127.0.0.1:3000",
        title="Juice Shop",
        text="Authorized local application",
        links=["http://127.0.0.1:3000/login"],
        forms=["POST http://127.0.0.1:3000/login"],
    )

    result = engine.record(observation)

    finding = store.add(
        Finding(
            title="Discovered Web Application Surface",
            description=(
                "A web application page and associated endpoints "
                "were observed during authorized discovery."
            ),
            target=result.target,
            severity=Severity.INFO,
            confidence=1.0,
            evidence=[
                f"Page title: {result.title}",
                f"Links discovered: {len(result.links)}",
                f"Forms discovered: {len(result.forms)}",
            ],
        )
    )

    assert store.summary()["total"] == 1
    assert finding.target == "http://127.0.0.1:3000"
    assert finding.severity == Severity.INFO
    assert len(finding.evidence) == 3

def test_discovery_result_can_be_converted_to_inventory_finding():
    from mythron.findings import Severity

    engine = DiscoveryEngine()

    result = engine.record(
        BrowserObservation(
            url="http://127.0.0.1:3000/",
            title="Juice Shop",
            text="Authorized local application",
            links=[
                "http://127.0.0.1:3000/login",
                "http://127.0.0.1:3000/search",
            ],
            forms=[
                "POST http://127.0.0.1:3000/rest/user/login",
            ],
        )
    )

    finding = engine.to_inventory_finding(result)

    assert finding.title == "Discovered Web Application Surface"
    assert finding.target == result.target
    assert finding.severity == Severity.INFO
    assert finding.confidence == 1.0
    assert len(finding.evidence) == 3

def test_discovery_can_store_inventory_finding():
    engine = DiscoveryEngine()

    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="Authorized local application",
        links=[
            "http://127.0.0.1:3000/login",
            "http://127.0.0.1:3000/search",
        ],
        forms=[
            "POST http://127.0.0.1:3000/rest/user/login",
        ],
    )

    result = engine.record(observation)

    finding = engine.store_inventory_finding(result)

    assert finding.title == "Discovered Web Application Surface"
    assert finding.target == result.target
    assert finding.severity.value == "INFO"
    assert finding.confidence == 1.0
    assert len(engine.findings().all()) == 1

def test_discovery_does_not_duplicate_same_inventory_finding():
    engine = DiscoveryEngine()

    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="Authorized local application",
        links=["http://127.0.0.1:3000/login"],
        forms=[],
    )

    result = engine.record(observation)

    engine.store_inventory_finding(result)
    engine.store_inventory_finding(result)

    assert len(engine.findings().all()) == 1

def test_discovery_stores_separate_findings_for_different_targets():
    engine = DiscoveryEngine()

    first = engine.record(
        BrowserObservation(
            url="http://127.0.0.1:3000/",
            title="Juice Shop",
            text="Home page",
            links=["http://127.0.0.1:3000/login"],
            forms=[],
        )
    )

    second = engine.record(
        BrowserObservation(
            url="http://127.0.0.1:3000/login",
            title="Login",
            text="Login page",
            links=[],
            forms=["POST http://127.0.0.1:3000/rest/user/login"],
        )
    )

    first_finding = engine.store_inventory_finding(first)
    second_finding = engine.store_inventory_finding(second)

    findings = engine.findings().all()

    assert len(findings) == 2
    assert first_finding.target == first.target
    assert second_finding.target == second.target
    assert first_finding.target != second_finding.target
