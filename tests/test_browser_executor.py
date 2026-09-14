from mythron.approaches import AttemptStatus, Approach
from mythron.browser_executor import BrowserApproachExecutor


def test_browser_executor_name():
    executor = BrowserApproachExecutor()

    assert executor.name == "browser"


def test_browser_executor_supports_browser_inspect():
    executor = BrowserApproachExecutor()

    approach = Approach(
        name="browser_inspect",
        description="http://127.0.0.1:3000",
        relevance=1.0,
    )

    assert executor.can_execute(approach)


def test_browser_executor_rejects_unsupported_approach():
    executor = BrowserApproachExecutor()

    approach = Approach(
        name="ssh_brute",
        description="http://127.0.0.1:3000",
        relevance=1.0,
    )

    assert not executor.can_execute(approach)


def test_browser_executor_rejects_invalid_url():
    executor = BrowserApproachExecutor()

    approach = Approach(
        name="browser_inspect",
        description="ftp://127.0.0.1:3000",
        relevance=1.0,
    )

    result = executor.execute(approach)

    assert result.status == AttemptStatus.FAILED
    assert "HTTP/HTTPS" in result.result
    assert result.failure_reason


def test_browser_executor_inspects_local_juice_shop():
    executor = BrowserApproachExecutor()

    approach = Approach(
        name="browser_inspect",
        description="http://127.0.0.1:3000",
        relevance=1.0,
    )

    result = executor.execute(approach)

    assert result.status == AttemptStatus.SUCCEEDED
    assert "OWASP Juice Shop" in result.result
    assert any("OWASP Juice Shop" in item for item in result.observations)
