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
    forms: List[str] = field(default_factory=list)
    headers: dict[str, str] = field(default_factory=dict)

    def has_header(self, name: str) -> bool:
        """Return True when the response contains the given header."""
        requested = name.strip().lower()
        return any(
            header_name.strip().lower() == requested
            for header_name in self.headers
        )


class BrowserAgent:
    """Small controlled browser capability for page inspection."""

    def __init__(self, headless: bool = True) -> None:
        self._headless = headless
        self._playwright = None
        self._browser: Browser | None = None

    @property
    def is_started(self) -> bool:
        """Return True when the browser is currently running."""
        return self._browser is not None

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
            response = page.goto(url, wait_until="domcontentloaded")
            headers = dict(response.headers) if response is not None else {}

            links = page.locator("a").evaluate_all(
                """elements => elements
                .map(a => a.href)
                .filter(href => href)"""
            )

            forms = page.locator("form").evaluate_all(
                """elements => elements
                .map(form => ({
                    action: form.action || "",
                    method: (form.method || "get").toUpperCase()
                }))
                .map(form => `${form.method} ${form.action}`)"""
            )

            return BrowserObservation(
                url=page.url,
                title=page.title(),
                text=page.locator("body").inner_text(),
                links=links,
                forms=forms,
                headers=headers,
            )
        finally:
            page.close()
