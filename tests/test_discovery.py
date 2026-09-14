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
