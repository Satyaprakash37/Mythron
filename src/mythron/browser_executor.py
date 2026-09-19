"""MYTHRON Phase 5 — Browser approach executor."""

from mythron.approaches import AttemptStatus, Approach
from mythron.browser import BrowserAgent
from mythron.executors import ExecutionResult


class BrowserApproachExecutor:
    """Execute browser-inspection approaches through BrowserAgent."""

    SUPPORTED_APPROACHES = {
        "web_crawl",
        "browser_inspect",
    }

    def __init__(self, browser: BrowserAgent | None = None) -> None:
        self._browser = browser or BrowserAgent(headless=True)

    @property
    def name(self) -> str:
        return "browser"

    def can_execute(self, approach: Approach) -> bool:
        """Return True for supported browser approaches."""
        return approach.name in self.SUPPORTED_APPROACHES

    def execute(self, approach: Approach) -> ExecutionResult:
        """Inspect the URL supplied in the approach description."""
        if not self.can_execute(approach):
            return ExecutionResult(
                status=AttemptStatus.FAILED,
                result="Unsupported browser approach",
                failure_reason=f"Unsupported approach: {approach.name}",
            )

        url = approach.description.strip()
        if not url.startswith(("http://", "https://")):
            return ExecutionResult(
                status=AttemptStatus.FAILED,
                result="Browser approach requires an HTTP/HTTPS URL",
                failure_reason="Invalid browser target URL",
            )

        started_here = False

        try:
            if not self._browser.is_started:
                self._browser.start()
                started_here = True

            observation = self._browser.inspect(url)

            return ExecutionResult(
                status=AttemptStatus.SUCCEEDED,
                result=(
                    f"Inspected {observation.url}; "
                    f"title={observation.title!r}; "
                    f"links={len(observation.links)}"
                ),
                observations=[
                    f"URL: {observation.url}",
                    f"Title: {observation.title}",
                    f"Links discovered: {len(observation.links)}",
                    observation.text[:500],
                ],
                data=observation,
            )

        except Exception as exc:
            return ExecutionResult(
                status=AttemptStatus.FAILED,
                result="Browser inspection failed",
                failure_reason=str(exc),
            )

        finally:
            if started_here:
                self._browser.stop()
