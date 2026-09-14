"""MYTHRON Phase 4 — Controlled browser agent."""

from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse

from playwright.sync_api import Browser, sync_playwright


@dataclass
class BrowserObservation:
    """Structured observation returned by the browser agent."""

    url: str
    title: str
    text: str
    links: List[str] = field(default_factory=list)


class BrowserAgent:
    """Small controlled browser capability for page inspection."""

    def __init__(self, headless: bool = True) -> None:
        self._headless = headless
        self._playwright = None
        self._browser: Browser | None = None

    def start(self) -> None:
        """Start the Playwright browser."""
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(
            headless=self._headless
        )

    def stop(self) -> None:
        """Stop the browser and release resources."""
        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def inspect(self, url: str) -> BrowserObservation:
        """Navigate to a URL and return basic page observations."""
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Only HTTP and HTTPS URLs are allowed.")

        if self._browser is None:
            raise RuntimeError("BrowserAgent is not started.")

        page = self._browser.new_page()
        try:
            page.goto(url, wait_until="domcontentloaded")
            links = page.locator("a").evaluate_all(
                """elements => elements
                .map(a => a.href)
                .filter(href => href)"""
            )

            return BrowserObservation(
                url=page.url,
                title=page.title(),
                text=page.locator("body").inner_text(),
                links=links,
            )
        finally:
            page.close()
