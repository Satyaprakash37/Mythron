from mythron.browser import BrowserAgent, BrowserObservation


def test_browser_agent_inspects_page():
    agent = BrowserAgent(headless=True)
    agent.start()

    try:
        observation = agent.inspect("https://example.com")

        assert observation.title == "Example Domain"
        assert observation.url.startswith("https://example.com")
        assert "Example Domain" in observation.text
        assert len(observation.links) >= 1
    finally:
        agent.stop()


def test_browser_rejects_invalid_scheme():
    agent = BrowserAgent(headless=True)

    try:
        agent.start()

        try:
            agent.inspect("ftp://example.com")
            assert False, "Expected ValueError"
        except ValueError as exc:
            assert "HTTP and HTTPS" in str(exc)
    finally:
        agent.stop()


def test_browser_requires_start():
    agent = BrowserAgent(headless=True)

    try:
        agent.inspect("https://example.com")
        assert False, "Expected RuntimeError"
    except RuntimeError as exc:
        assert "not started" in str(exc)

def test_browser_agent_discovers_forms():
    agent = BrowserAgent(headless=True)
    agent.start()

    try:
        observation = agent.inspect("https://example.com")

        assert hasattr(observation, "forms")
        assert isinstance(observation.forms, list)
    finally:
        agent.stop()


def test_browser_observation_captures_response_headers():
    observation = BrowserObservation(
        url="https://example.com",
        title="Example Domain",
        text="Example Domain",
        headers={
            "content-type": "text/html",
            "x-frame-options": "DENY",
        },
    )

    assert observation.headers["content-type"] == "text/html"
    assert observation.headers["x-frame-options"] == "DENY"


def test_browser_observation_can_report_security_header_presence():
    observation = BrowserObservation(
        url="http://127.0.0.1:3000/",
        title="Juice Shop",
        text="",
        headers={
            "x-content-type-options": "nosniff",
        },
    )

    assert observation.has_header("x-content-type-options")
    assert not observation.has_header("content-security-policy")
